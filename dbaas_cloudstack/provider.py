# -*- coding: utf-8 -*-
from client import CloudStackClient
from base64 import b64encode
import logging
from django.template import Context, Template
from time import sleep


LOG = logging.getLogger(__name__)

class CloudStackProvider(object):

    def __init__(self, credentials):
        self.api = self.authenticate(credentials= credentials)


    def authenticate(self, credentials):
        try:
            LOG.info("Conecting with cloudstack...")
            return CloudStackClient(credentials.endpoint, credentials.token, credentials.secret)
        except Exception, e:
            LOG.warning("We could not authenticate with cloudstack because %s" % e)
            return None


    def destroy_virtual_machine(self, project_id, environment, vm_id):
        try:
            request = { 
                              'projectid': project_id,
                              'id': vm_id
                            }

            response = self.api.destroyVirtualMachine('GET',request)
            if 'jobid' in response:
                query_async= self.query_async_job( jobid= response['jobid'])
                if query_async==True:
                    LOG.info("VirtualMachine destroyed!")
                    return True
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %i, %s" % (response['errorcode'], response['errortext']))
                return None

        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)
            return None


    def build_user_data(self, contextdict, userdata):
        try:
            LOG.info(str(contextdict))

            context = Context(contextdict)
            
            template = Template(userdata)
            return template.render(context)
        except Exception, e:
            LOG.warning("We could build the userdata because %s" % e)
            return False


    def update_userdata(self, vm_id , contextdict, userdata):
        try:
            request = { 'id': vm_id, 
                              'userdata': b64encode(self.build_user_data(contextdict= contextdict, userdata= userdata))
                            }
            self.api.updateVirtualMachine('POST', request)
            return True
        except Exception, e:
            LOG.warning("We could update the userdata because %s" % e)
            return False


    def reserve_ip(self, project_id, vm_id, wait=20):
        try:
            request = {'projectid': '%s' % (project_id), 'id':'%s' % (vm_id) }
            response = self.api.listVirtualMachines('GET',request)
            
            nicid = response['virtualmachine'][0]['nic'][0]['id']
            self.api.addIpToNic('GET', {'nicid': nicid})

            sleep(wait)    
            
            request['virtualmachineid'] = vm_id
            response = self.api.listNics('GET',request)
            
            secondary_ip = response['nic'][0]['secondaryip'][0]['ipaddress']
            cs_ip_id = response['nic'][0]['secondaryip'][0]['id']
            
            LOG.info('Secondary ip %s for vm %s' % (secondary_ip, vm_id))
            return secondary_ip, cs_ip_id

        except Exception, e:
            LOG.warning("We could reserve ip because %s" % e)
            return None


    def query_async_job(self, jobid, retries=20, wait=0):
        try:
            for attempt in range(0, retries):
                if attempt>0 and wait>0:
                    sleep(wait)

                LOG.info("Cheking async job... attempt number %i..." % attempt + 1)

                job = self.api.queryAsyncJobResult('POST', {'jobid': jobid})
                if job['jobstatus']==1:
                    return True
                elif job['jobstatus']==2 or (attempt == retries-1):
                    return False
        
        except Exception, e:
            LOG.warning("We caught an exception: %s ." % (e))
            return None


    def deploy_virtual_machine(self, planattr, project_id, vmname, ):
        try:
            request = { 'serviceofferingid': planattr.serviceofferingid, 
                  'templateid': planattr.templateid, 
                  'zoneid': planattr.zoneid,
                  'networkids': planattr.networkid,
                  'projectid': project_id,
                  'name': vmname,
            }

            response = self.api.deployVirtualMachine('POST',request)
            LOG.info(" CloudStack response %s" % (response))

            if 'jobid' in response:
                query_async= self.query_async_job( jobid= response['jobid'])
                if query_async==True:
                    LOG.info("VirtualMachine created!")
                    return response
                else:
                    return False
            else:
                LOG.warning("Something ocurred on cloudstack: %i, %s" % (response['errorcode'], response['errortext']))
                return None

        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)

            if 'id' in response:
                LOG.info("Destroying VirtualMachine %s on cloudstack." % response['id'])
                self.api.destroyVirtualMachine('POST',{'id': response['id']})
                LOG.info("VirtualMachine destroyed!")
            return None


    def remove_secondary_ips(self, cloudstack_ip_ids):
        try:
            for cloudstack_ip_id in cloudstack_ip_ids:
                LOG.info("Removing secondary ip (id: %s)" % (cloudstack_ip_id))
                self.api.removeIpFromNic('POST',{'id': cloudstack_ip_id})
        except Exception, e:
            LOG.warning("We could remove the secondary ip because %s" % e)
            return None
