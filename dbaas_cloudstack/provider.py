# -*- coding: utf-8 -*-
from client import CloudStackClient
from base64 import b64encode
import logging
from django.template import Context, Template
from time import sleep


LOG = logging.getLogger(__name__)


class CloudStackProvider(object):
    def __init__(self, credentials, networkapi_credentials=None):
        self.api = self.authenticate(credentials=credentials)
        self.networkapi_credentials = networkapi_credentials

    def authenticate(self, credentials):
        try:
            LOG.info("Conecting with cloudstack...")
            return CloudStackClient(credentials.endpoint, credentials.token, credentials.secret)
        except Exception as e:
            LOG.warning(
                "We could not authenticate with cloudstack because %s" % e)
            return None

    def destroy_virtual_machine(self, project_id, environment, vm_id):
        try:
            request = {'id': vm_id}

            response = self.api.destroyVirtualMachine('GET', request)
            if 'jobid' in response:
                query_async = self.query_async_job(jobid=response['jobid'])
                if query_async is True:
                    LOG.info("VirtualMachine destroyed!")
                    return True
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %s, %s" %
                            (response['errorcode'], response['errortext']))
                return None

        except Exception as e:
            LOG.warning(
                "We could not create the VirtualMachine because %s" % e)
            return None

    def build_user_data(self, contextdict, userdata):
        try:
            LOG.info(str(contextdict))

            context = Context(contextdict)

            template = Template(userdata)
            return template.render(context)
        except Exception as e:
            LOG.warning("We could build the userdata because %s" % e)
            return False

    def update_userdata(self, vm_id, contextdict, userdata):
        try:
            request = {'id': vm_id,
                       'userdata': b64encode(self.build_user_data(contextdict=contextdict, userdata=userdata))
                       }
            self.api.updateVirtualMachine('POST', request)
            return True
        except Exception as e:
            LOG.warning("We could update the userdata because %s" % e)
            return False

    def reserve_ip(self, project_id, vm_id, wait=20):
        try:
            request = {'projectid': project_id, 'id': vm_id}
            response = self.api.listVirtualMachines('GET', request)

            nicid = response['virtualmachine'][0]['nic'][0]['id']
            self.api.addIpToNic('GET', {'nicid': nicid})

            sleep(wait)

            request['virtualmachineid'] = vm_id
            response = self.api.listNics('GET', request)

            secondary_ip = response['nic'][0]['secondaryip'][0]['ipaddress']
            cs_ip_id = response['nic'][0]['secondaryip'][0]['id']

            LOG.info('Secondary ip %s for vm %s' % (secondary_ip, vm_id))
            return {'secondary_ip': secondary_ip, 'cs_ip_id': cs_ip_id}

        except Exception as e:
            LOG.warning("We could reserve ip because %s" % e)
            return None

    def query_async_job(self, jobid, retries=90, wait=10):
        try:
            for attempt in range(0, retries):
                if attempt > 0 and wait > 0:
                    sleep(wait)

                LOG.info("Cheking async job... attempt number %s..." %
                         str(attempt + 1))

                job = self.api.queryAsyncJobResult('POST', {'jobid': jobid})
                if job['jobstatus'] == 1:
                    return True
                elif job['jobstatus'] == 2 or (attempt == retries - 1):
                    LOG.warning(
                        "Something ocurred on cloudstack: {}".format(job))
                    return False

        except Exception as e:
            LOG.warning("We caught an exception: %s ." % (e))
            return None

    def deploy_virtual_machine(self, offering, bundle, project_id, vmname, affinity_group_id=None):
        try:
            request = {'serviceofferingid': offering,
                       'templateid': bundle.templateid,
                       'zoneid': bundle.zoneid,
                       'networkids': bundle.networkid,
                       'projectid': project_id,
                       'name': vmname,
                       }

            if affinity_group_id:
                request['affinitygroupids'] = affinity_group_id
                del request['projectid']

            response = self.api.deployVirtualMachine('POST', request)
            LOG.info(" CloudStack response %s" % (response))

            if 'jobid' in response:
                query_async = self.query_async_job(jobid=response['jobid'])
                if query_async is True:
                    LOG.info("VirtualMachine created!")
                    if affinity_group_id:
                        request = {'id': response['id']}
                    else:
                        request = {
                            'projectid': project_id, 'id': response['id']}
                    return self.api.listVirtualMachines('GET', request)
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %s, %s" %
                            (response['errorcode'], response['errortext']))
                return None

        except Exception as e:
            LOG.warning(
                "We could not create the VirtualMachine because %s" % e)
            return None

    def remove_secondary_ips(self, cloudstack_ip_id):
        try:
            LOG.info("Removing secondary ip (id: %s)" % (cloudstack_ip_id))
            self.api.removeIpFromNic('POST', {'id': cloudstack_ip_id})
            return True
        except Exception as e:
            LOG.warning("We could remove the secondary ip because %s" % e)
            return None

    def stop_virtual_machine(self, vm_id):
        try:
            LOG.info("Stoping Virtualmachine (id: %s)" % (vm_id))
            response = self.api.stopVirtualMachine('POST', {'id': vm_id})

            if 'jobid' in response:
                query_async = self.query_async_job(jobid=response['jobid'])
                if query_async is True:
                    LOG.info("VirtualMachine stoped!")
                    return True
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %s, %s" %
                            (response['errorcode'], response['errortext']))
                return None

        except Exception as e:
            LOG.warning("We could stop the virtualmachine because %s" % e)
            return None

    def start_virtual_machine(self, vm_id):
        try:
            LOG.info("Starting Virtualmachine (id: %s)" % (vm_id))
            response = self.api.startVirtualMachine('POST', {'id': vm_id})

            if 'jobid' in response:
                query_async = self.query_async_job(jobid=response['jobid'])
                if query_async is True:
                    LOG.info("VirtualMachine started!")
                    return True
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %s, %s" %
                            (response['errorcode'], response['errortext']))
                return None

        except Exception as e:
            LOG.warning("We could start the virtualmachine because %s" % e)
            return None

    def reboot_virtual_machine(self, vm_id):
        stoped = self.stop_virtual_machine(vm_id)

        if not stoped:
            return False

        started = self.start_virtual_machine(vm_id)

        if not started:
            return False

        return True

    def list_service_offerings_for_vm(self, vm_id):
        try:
            LOG.info("Listing service offerings for vm (id: %s)" % (vm_id))

            response = self.api.listServiceOfferings(
                'GET', {'virtualmachineid': vm_id})

            return response
        except Exception as e:
            LOG.warning("We could not retrieve the service offering %s" % e)
            return None

    def get_vm_offering_id(self, vm_id, project_id, affinity_group_id=None):
        try:
            LOG.info("Listing service offerings for vm (id: %s)" % (vm_id))

            request = {'projectid': project_id, 'id': vm_id}

            if affinity_group_id:
                request['affinitygroupids'] = affinity_group_id
                del request['projectid']

            response = self.api.listVirtualMachines('GET', request)

            return response['virtualmachine'][0]['serviceofferingid']
        except Exception as e:
            LOG.warning("We could not retrieve the vm offeringid %s" % e)
            return None

    def get_vm_network_id(self, vm_id, project_id, affinity_group_id=None):
        try:
            LOG.info("Listing networkid for vm (id: %s)" % (vm_id))

            request = {'projectid': project_id, 'id': vm_id}

            if affinity_group_id:
                request['affinitygroupids'] = affinity_group_id
                del request['projectid']

            response = self.api.listVirtualMachines('GET', request)

            return response['virtualmachine'][0]['nic'][0]['networkid']
        except Exception as e:
            LOG.warning("We could not retrieve the vm networkid %s" % e)
            return None

    def get_vm_ostype(self, vm_id, project_id, affinity_group_id=None):
        try:
            LOG.info("Listing ostype for vm (id: %s)" % (vm_id))

            request = {'projectid': project_id, 'id': vm_id}
            if affinity_group_id:
                request['affinitygroupids'] = affinity_group_id
                del request['projectid']

            response = self.api.listVirtualMachines('GET', request)
            ostypeid = response['virtualmachine'][0]['ostypeid']
            LOG.info("ostypeid = {}".format(ostypeid))
            os_type = self.api.listOsTypes('GET', {'id': str(ostypeid)})

            return os_type['ostype'][0]['description']

        except Exception as e:
            LOG.warning("We could not retrieve ostype for vm. Error: %s" % e)
            return None

    def change_service_for_vm(self, vm_id, serviceofferingid):
        try:
            LOG.info("Changing service offering (id: %s) for virtualmachine, (id: %s)" % (
                serviceofferingid, vm_id))
            response = self.api.scaleVirtualMachine(
                'POST', {'id': vm_id, 'serviceofferingid': serviceofferingid})

            if 'jobid' in response:
                query_async = self.query_async_job(jobid=response['jobid'])
                if query_async is True:
                    LOG.info("Service Offering changed!")
                    return True
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %s, %s" %
                            (response['errorcode'], response['errortext']))
                return None

        except Exception as e:
            LOG.warning("We could change the service offering because %s" % e)
            return None

    def change_offering_and_reboot(self, vm_id, serviceofferingid):
        stoped = self.stop_virtual_machine(vm_id)

        if not stoped:
            return False

        offering_changed = self.change_service_for_vm(vm_id, serviceofferingid)

        if not offering_changed:
            return False

        started = self.start_virtual_machine(vm_id)

        if not started:
            return False

        return True

    def register_networkapi_equipment(self, equipment_name):
        from networkapiclient.Equipamento import Equipamento

        try:
            LOG.info("Register database infra as equipment on network api...")
            equipmentAPI = Equipamento(networkapi_url=self.networkapi_credentials.endpoint,
                                       user=self.networkapi_credentials.user,
                                       password=self.networkapi_credentials.password)

            equipment = equipmentAPI.inserir(name=equipment_name,
                                             id_equipment_type=self.networkapi_credentials.get_parameter_by_name(
                                                 'id_equipment_type'),
                                             id_model=self.networkapi_credentials.get_parameter_by_name(
                                                 'id_model'),
                                             id_group=self.networkapi_credentials.get_parameter_by_name('id_group'))

            LOG.info("equipment = %s " % repr(equipment))
            return equipment['equipamento']['id']
        except Exception as e:
            LOG.warning(
                "We could not register networkapi equipment because %s" % e)
            return None

    def remove_networkapi_equipment(self, equipment_id):
        from networkapiclient.Equipamento import Equipamento

        try:
            LOG.info(
                "Removing networkapi equipment [ id = %s ]" % equipment_id)
            equipmentAPI = Equipamento(networkapi_url=self.networkapi_credentials.endpoint,
                                       user=self.networkapi_credentials.user,
                                       password=self.networkapi_credentials.password)
            equipmentAPI.remover(id_equipamento=equipment_id)
            return True
        except Exception as e:
            LOG.warning(
                "We could not remove networkapi equipment because %s" % e)
            return None

    def register_networkapi_ip(self, equipment_id, ip, ip_desc):
        from networkapiclient.Ip import Ip
        from networkapiclient.Vlan import Vlan
        from networkapiclient.Pagination import Pagination

        try:
            LOG.info("Register ip on network api...")
            LOG.info("equipment_id=%s, ip=%s, ip_desc=%s" %
                     (equipment_id, ip, ip_desc))

            network = '.'.join(ip.split('.')[:-1]) + '.0/24'

            pagination = Pagination(0, 25, "", "", "")
            vlanAPI = Vlan(networkapi_url=self.networkapi_credentials.endpoint,
                           user=self.networkapi_credentials.user,
                           password=self.networkapi_credentials.password)

            vlans = vlanAPI.find_vlans(
                '', '', 0, '', '', network, 0, 0, '', pagination)
            vlan = vlans['vlan'][0]['redeipv4'][0]['id']
            LOG.info('Vlan = %s', vlan)

            ipAPI = Ip(networkapi_url=self.networkapi_credentials.endpoint,
                       user=self.networkapi_credentials.user,
                       password=self.networkapi_credentials.password)

            networkapi_ip = ipAPI.save_ipv4(ip4=ip,
                                            id_equip=equipment_id,
                                            descricao=ip_desc,
                                            id_net=vlan)

            LOG.info("networkapi_ip = %s " % repr(networkapi_ip))
            return networkapi_ip['ip']['id']
        except Exception as e:
            LOG.warning("We could not register networkapi ip because %s" % e)
            return None

    def remove_networkapi_ip(self, equipment_id, ip_id):
        from networkapiclient.Equipamento import Equipamento

        try:
            LOG.info(
                "Removing networkapi equipment [ id = %s ]" % equipment_id)
            equipmentAPI = Equipamento(networkapi_url=self.networkapi_credentials.endpoint,
                                       user=self.networkapi_credentials.user,
                                       password=self.networkapi_credentials.password)
            equipmentAPI.remover_ip(id_equipamento=equipment_id, id_ip=ip_id)
            return True
        except Exception as e:
            LOG.warning(
                "We could not remove networkapi equipment because %s" % e)
            return None
