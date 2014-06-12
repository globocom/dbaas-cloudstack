# -*- coding: utf-8 -*-
from client import CloudStackClient
from base64 import b64encode
import logging
from models import PlanAttr
from django.template import Context, Template
from time import sleep


LOG = logging.getLogger(__name__)

class CloudStackProvider(object):

    def __init__(self, environment):
        self.api = self.authenticate(environment= environment)


    def authenticate(self, environment):
        try:
            LOG.info("Conecting with cloudstack...")
            credentials = self.get_credentials(environment= environment)
            return CloudStackClient(credentials.endpoint, credentials.token, credentials.secret)
        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)
            return None


    def destroy_virtual_machine(self, environment, vm_id):
        try:
            project_id = self.get_credentials(environment= environment).project
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


    def build_user_data(self, contextdict, plan):
        try:
            planattr = PlanAttr.objects.get(plan=plan)
            
            LOG.info(str(contextdict))

            context = Context(contextdict)
            
            template = Template(planattr.userdata)
            return template.render(context)
        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)
            return False


    def update_userdata(self, vm_id , plan, contextdict):
        try:
            request = { 'id': vm_id, 
                              'userdata': b64encode(self.build_user_data(contextdict, plan))
                            }
            self.api.updateVirtualMachine('POST', request)
            return True
        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)
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
            LOG.warning("We could not create the VirtualMachine because %s" % e)
            return False


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
            return False


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
            LOG.warning("We could not create the VirtualMachine because %s" % e)
            return None

    # @classmethod
    # def add_dns_record(self, databaseinfra, name, ip, type):
    #     planattr = dnsapi_PlanAttr.objects.get(dbaas_plan=databaseinfra.plan)
    #     if planattr.dnsapi_database_sufix:
    #         sufix = '.' + planattr.dnsapi_database_sufix
    #     else:
    #         sufix = ''
        
    #     if type == DNSAPI_HOST:
    #         domain = planattr.dnsapi_vm_domain
    #     else:
    #         domain = planattr.dnsapi_database_domain
    #         name += sufix
        
    #     databaseinfradnslist = dnsapi_DatabaseInfraDNSList(
    #         databaseinfra = databaseinfra.id,
    #         name = name,
    #         domain = domain,
    #         ip = ip,
    #         type = type)
    #     databaseinfradnslist.save()
        
    #     dnsname = '%s.%s' % (name, domain)
    #     return dnsname

    # @classmethod
    # def del_dns_record(self, databaseinfra):
    #     dnsapi_DatabaseInfraDNSList.objects.filter(databaseinfra=databaseinfra.id).delete()


    # @classmethod
    # @transaction.commit_on_success
    # def destroy_instance(self, database, *args, **kwargs):
    #     if database.is_in_quarantine:
    #         super(Database, database).delete(*args, **kwargs)
    #         LOG.warning("Deleting the host on cloudstack...")
    #         self.destroy_dependencies(databaseinfra= database.databaseinfra)
            
    #     else:
    #         LOG.warning("Putting database %s in quarantine" % database.name)
    #         database.is_in_quarantine=True
    #         database.save()
    #         if database.credentials.exists():
    #             for credential in database.credentials.all():
    #                 new_password = make_db_random_password()
    #                 new_credential = targetdbCredential.objects.get(pk=credential.id)
    #                 new_credential.password = new_password
    #                 new_credential.save()

    #                 instance = factory_for(database.databaseinfra)
    #                 instance.update_user(new_credential)

    # @classmethod
    # def destroy_dependencies(self, databaseinfra):
    #     try :
    #         plan = databaseinfra.plan
    #         environment = databaseinfra.environment

    #         instances = list(databaseinfra.instances.all())
    #         LOG.debug("DatabaseInfra %s instances %s" % (databaseinfra, instances))
    #         for instance in instances:
    #             host = instance.hostname
    #             host_attr = HostAttr.objects.filter(host= host)[0]

    #             self.destroy_nfsaas(host= host, host_attr= host_attr, environment= environment,plan= plan)
    #             self.destroy_vm(environment= environment, instance= instance)
    #             FlipperProvider().destroy_flipper_dependencies(masterpairname=databaseinfra.name, environment=environment)

    #             if instances.index(instance) == len(instances)-1:
    #                 self.destroy_dbaas_dependencies(databaseinfra= databaseinfra)
                    
    #     except Exception, e:
    #         LOG.warning("We could not destroy the infractructure.  %s :(" % e)
    
    # @classmethod
    # def destroy_nfsaas(self, host, host_attr, environment, plan):
    #     LOG.info("Remove all database files")
    #     self.run_script(host= host, host_attr= host_attr, command= "/opt/dbaas/scripts/dbaas_deletedatabasefiles.sh")
    
    #     LOG.info("Destroying storage (environment:%s, plan: %s, host:%s)!" % (environment, plan, host))
    #     StorageManager.destroy_disk(environment=environment, plan=plan, host=host)

    # @classmethod
    # def destroy_dbaas_dependencies(self, databaseinfra):
    #     for instance in databaseinfra.instances.all():
    #         host= instance.hostname

    #         NfsHostAttr.objects.filter(host= host).delete()
    #         LOG.info("Host custom nfsaas attrs destroyed!")

    #         HostAttr.objects.filter(host= host).delete()
    #         LOG.info("Host custom cloudstack attrs destroyed!")

    #         host.delete()
    #         LOG.info("Host destroyed!")

    #         instance.delete()
    #         LOG.info("Instance destroyed!")

    #     if databaseinfra.plan.is_ha:
    #         databaseinfra.cs_dbinfra_attributes.all().delete()
    #         LOG.info("DatabaseInfra custom cloudstack attributes detroyed!")

    #     databaseinfra.delete()
    #     LOG.info("DatabaseInfra destroyed!")

    #     paramiko.HostKeys().clear()
    #     LOG.info("Removing key from known hosts!")
    #     LOG.info("Finished!")


    # @classmethod
    # @transaction.commit_on_success
    # def create_instance_cluster(self, plan, environment, name, task):
    
    #     LOG.info("Provisioning new host on cloud portal with options %s %s..." % (plan, environment))
    #     task.update_status_for(task.STATUS_RUNNING, details="Provisioning new host on cloud portal with options %s %s..." % (plan, environment))
        
    #     api = self.auth(environment= environment)
    #     planattr = PlanAttr.objects.get(plan=plan)
    #     project_id = self.get_credentials(environment= environment).project
    #     names = self.gen_infra_name(name, 2)
    #     infraname = names["infra"]
        
    #     databaseinfra = self.build_databaseinfra(infraname= infraname, plan= plan, environment= environment)

    #     instances = []

    #     for vmname in names["vms"]:
    #         instance = self.create_vm(api, planattr, project_id, infraname, vmname, plan, environment, True, databaseinfra)

    #         if instance==None:
    #             for i in instances:

    #                 LOG.warning("Destroying cloudstack cluster instance!")
    #                 task.update_status_for(task.STATUS_RUNNING, details="Destroying cloudstack cluster instance!")
    #                 self.destroy_vm(environment= environment, instance=i)
    #                 i.hostname.delete()

    #             databaseinfra.delete()
    #             return None
    #         else:
    #             instances.append(instance)

    #     databasesinfraattr = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra)
    #     if databasesinfraattr[0].is_write:
    #         write_ip = databasesinfraattr[0].ip
    #         read_ip = databasesinfraattr[1].ip
    #     else:
    #         write_ip = databasesinfraattr[1].ip
    #         read_ip = databasesinfraattr[0].ip
    #     contextdict = {
    #         'EXPORTPATH': None,
    #         'SERVERID': None,
    #         'DBPASSWORD': self.get_mysql_credentials(environment=environment).password,
    #         'IPMASTER': None,
    #         'IPWRITE': write_ip,
    #         'IPREAD': read_ip,
    #         'MASTERPAIRNAME': infraname,
    #         'HOST01': instances[0].hostname,
    #         'HOST02': instances[1].hostname,
    #         'INSTANCE01': instances[0],
    #         'INSTANCE02': instances[1],
    #         'SECOND_SCRIPT_FILE': '/opt/dbaas/scripts/dbaas_second_script.sh',
    #     }

    #     try:
    #         self.build_dependencies(contextdict=contextdict, host=contextdict['HOST01'], serverid=1, master=contextdict['HOST02'].address, 
    #                                      environment=environment, plan=plan, databaseinfra=databaseinfra, api=api)

    #         self.build_dependencies(contextdict=contextdict, host=contextdict['HOST02'], serverid=2, master=contextdict['HOST01'].address, 
    #                                      environment=environment, plan=plan, databaseinfra=databaseinfra, api=api)
            
    #         if self.run_script(contextdict['HOST01'], contextdict['SECOND_SCRIPT_FILE'])==0:
    #             if self.run_script(contextdict['HOST02'], contextdict['SECOND_SCRIPT_FILE'])==0:
    #                 pass
    #             else:
    #                 raise Exception, "We could not run the script on host 2"
    #                 task.update_status_for(task.STATUS_RUNNING, details="We could not run the script on host 2")
    #         else:
    #             raise Exception, "We could not run the script on host 1"
    #     except Exception, e:
    #         for instance in instances:
    #             LOG.warning("We could not deploy your cluster because: %s" % e)
    #             task.update_status_for(task.STATUS_RUNNING, details="We could not deploy your cluster because: %s" % e)

    #             LOG.info("Remove all database files")
    #             self.run_script(instance.hostname, "/opt/dbaas/scripts/dbaas_deletedatabasefiles.sh")
    #             StorageManager.destroy_disk(environment= environment, plan= plan, host= instance.hostname)
    #             self.remove_secondary_ips(api, databaseinfra)
    #             api.destroyVirtualMachine('POST',{'id': "%s" % (instance.hostname.cs_host_attributes.all()[0].vm_id)})
    #             instance.hostname.delete()            
    #             flipper = FlipperProvider()
    #             flipper.destroy_flipper_dependencies(masterpairname= databaseinfra.name, environment= environment)
    #         databaseinfra.delete()
    #         return None
        
    #     return databaseinfra

    

    # @classmethod
    # def build_nfsaas(self, environment, plan, host):
    #     return StorageManager.create_disk(environment=environment, plan=plan, host=host)

    # @classmethod
    # def build_flipper(self, contextdict, environment):
    #     flipper = FlipperProvider()
    #     flipper.create_flipper_dependencies(masterpairname= contextdict['MASTERPAIRNAME'], 
    #                                                             readip= contextdict['IPREAD'], 
    #                                                             writeip= contextdict['IPWRITE'], 
    #                                                             hostname1= contextdict['HOST01'].address, 
    #                                                             hostname2= contextdict['HOST02'].address, 
    #                                                             environment= environment)



    # @classmethod
    # @transaction.commit_on_success
    # def build_dependencies(self, contextdict, host, serverid, master, environment, plan, databaseinfra, api):
    #     try:
    #         disk = self.build_nfsaas(environment= environment, plan= plan, host= host)

    #         contextdict['EXPORTPATH'] = disk['path']
    #         contextdict['SERVERID'] = serverid
    #         contextdict['IPMASTER'] = master

    #         self.update_userdata(host= host, api= api, plan= plan, contextdict= contextdict)

    #         if serverid==1:
    #             self.build_flipper(contextdict= contextdict, environment= environment)
            
    #         contextdict['INSTANCE01'].databaseinfra = databaseinfra
    #         contextdict['INSTANCE01'].save()

    #         contextdict['INSTANCE02'].databaseinfra = databaseinfra
    #         contextdict['INSTANCE02'].save()

    #         LOG.info("Instance created!")
            
    #         return databaseinfra
    #     except Exception, e:
    #         print e

    # @classmethod
    # @transaction.commit_on_success
    # def create_instance(self, plan, environment, name):
    
    #     LOG.info("Provisioning new host on cloud portal with options %s %s..." % (plan, environment))
    #     api = self.auth(environment= environment)
    #     planattr = PlanAttr.objects.get(plan=plan)
    #     project_id = self.get_credentials(environment= environment).project
    
        
    #     instance = self.create_vm(api, planattr, project_id, infraname, vmname, plan, environment, False, databaseinfra)
    #     if instance is None:
    #         databaseinfra.delete()
    #         return None
        
        
    #     databaseinfra.endpoint = instance.address + ":%i" %(instance.port)
    #     databaseinfra.endpoint_dns = instance.dns + ":%i" %(instance.port)
    #     databaseinfra.save()
    #     instance.databaseinfra = databaseinfra
    #     instance.save()
    #     LOG.info("Instance created!")
        
    #     return databaseinfra

    # @classmethod
    # def build_databaseinfra(self, infraname, plan, environment):
    #     mysql_credentials = self.get_mysql_credentials(environment=environment)
    #     databaseinfra = DatabaseInfra()
    #     databaseinfra.name = infraname
    #     databaseinfra.user  = mysql_credentials.user
    #     databaseinfra.password = mysql_credentials.password
    #     databaseinfra.engine = plan.engine_type.engines.all()[0]
    #     databaseinfra.plan = plan
    #     databaseinfra.environment = environment
    #     databaseinfra.capacity = 1
    #     databaseinfra.per_database_size_mbytes=0
    #     databaseinfra.save()
    #     LOG.info("DatabaseInfra created!")
    #     return databaseinfra



            # request = {'projectid': '%s' % (project_id), 'id':'%s' % (response['id']) }
            # host_attr = HostAttr()
            # host_attr.vm_id = response['id']
            # response = api.listVirtualMachines('GET',request)
            # host = Host()
            # host.address = response['virtualmachine'][0]['nic'][0]['ipaddress']
            # host.hostname = self.add_dns_record(databaseinfra=databaseinfra, name=vmname, ip=host.address, type=DNSAPI_HOST)
            # host.cloud_portal_host = True
            # host.save()
            # LOG.info("Host created!")
            # vm_credentials = self.get_vm_credentials(environment=environment)
            # host_attr.vm_user = vm_credentials.user
            # host_attr.vm_password = vm_credentials.password
            # host_attr.host = host
            # host_attr.save()
            # LOG.info("Host attrs custom attributes created!")
            # instance = Instance()
            # instance.address = host.address
            # instance.dns = self.add_dns_record(databaseinfra=databaseinfra, name=vmname, ip=instance.address, type=DNSAPI_INSTANCE)
            # instance.port = 3306
            # instance.is_active = True
            # instance.is_arbiter = False
            # instance.hostname = host
            # ssh_ok = self.check_ssh(host)
            # if  ssh_ok:
            #     if cluster:
            #         databaseinfraattr = DatabaseInfraAttr()
            #         total = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra).count()
            #         if total == 0:
            #             databaseinfraattr.is_write = True
            #             dnsname = databaseinfra.name
            #         else:
            #             databaseinfraattr.is_write = False
            #             dnsname = databaseinfra.name + '-r'                 
            #         databaseinfraattr.ip , databaseinfraattr.cs_ip_id= self.reserve_ip(project_id= project_id, host_attr= host_attr, api= api)
            #         databaseinfraattr.databaseinfra = databaseinfra
            #         databaseinfraattr.dns = self.add_dns_record(databaseinfra=databaseinfra, name=dnsname, ip=databaseinfraattr.ip, type=DNSAPI_FLIPPER)
            #         databaseinfraattr.save()
            #         if total == 0:
            #             databaseinfra.endpoint = databaseinfraattr.ip + ":%i" %(3306)
            #             databaseinfra.endpoint_dns = databaseinfraattr.dns + ":%i" %(3306)
            #             databaseinfra.save()
            #     else:
            #         disk = self.build_nfsaas(environment=environment, plan=plan, host=host)
            #         self.update_userdata(host= host, api= api, plan= plan, contextdict={"EXPORTPATH": disk['path']})
            #     return instance
            # else:
            #     raise Exception, "Maximum number of login attempts!"
            # except Exception, e:
            #     LOG.warning("We could not create the VirtualMachine because %s" % e)

            #     if 'virtualmachine' in response:
            #         if 'databaseinfraattr' in locals() and databaseinfraattr:
            #             self.remove_secondary_ips(api, databaseinfraattr.databaseinfra)
            #         vm_id = response['virtualmachine'][0]['id']
            #         LOG.info("Destroying VirtualMachine %s on cloudstack." % (vm_id))
            #         api.destroyVirtualMachine('POST',{'id': "%s" % (vm_id)})
            #         LOG.info("VirtualMachine destroyed!")
            #         if 'disk' in locals() and disk:
            #             LOG.info("Destroying storage...")
            #             StorageManager.destroy_disk(environment= environment, plan= plan, host= host)
            #             LOG.info("Storage destroyed!")
            #         self.del_dns_record(databaseinfra)
            #     else:
            #        LOG.warning("Something ocurred on cloudstack: %i, %s" % (response['errorcode'], response['errortext']))
                
            #     return None
