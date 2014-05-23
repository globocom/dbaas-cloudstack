# -*- coding: utf-8 -*-
from client import CloudStackClient
from django.db import transaction
from physical.models import DatabaseInfra, Instance, Host
from logical.models import Credential as targetdbCredential
from logical.models import Database
from util import make_db_random_password
from drivers import factory_for
from .models import PlanAttr, HostAttr, DatabaseInfraAttr
from base64 import b64encode
import logging
from integrations.storage.manager import StorageManager
from dbaas_flipper.provider import FlipperProvider
from dbaas_credentials.credential import Credential
from dbaas_credentials.models import CredentialType
from dbaas_dnsapi.models import DatabaseInfraDNSList as dnsapi_DatabaseInfraDNSList, PlanAttr as dnsapi_PlanAttr
from dbaas_dnsapi.models import HOST as DNSAPI_HOST, INSTANCE as DNSAPI_INSTANCE, FLIPPER as DNSAPI_FLIPPER

from django.template import Context, Template
from time import sleep
import paramiko
import socket

LOG = logging.getLogger(__name__)

class CloudStackProvider(object):
    
    @classmethod
    #@transaction.commit_on_success
    def add_dns_record(self, databaseinfra, name, ip, type):
        planattr = dnsapi_PlanAttr.objects.get(dbaas_plan=databaseinfra.plan)
        if planattr.dnsapi_database_sufix:
            sufix = '.' + planattr.dnsapi_database_sufix
        else:
            sufix = ''
        
        if type == DNSAPI_HOST:
            domain = planattr.dnsapi_vm_domain
        else:
            domain = planattr.dnsapi_database_domain
            name += sufix
        
        databaseinfradnslist = dnsapi_DatabaseInfraDNSList(
            databaseinfra = databaseinfra.id,
            name = name,
            domain = domain,
            ip = ip,
            type = type)
        databaseinfradnslist.save()
        
        dnsname = '%s.%s' % (name, domain)
        return dnsname

    @classmethod
    def del_dns_record(self, databaseinfra):
        dnsapi_DatabaseInfraDNSList.objects.filter(databaseinfra=databaseinfra.id).delete()
    
    @classmethod
    def get_credentials(self, environment):
        LOG.info("Getting credentials...")
        integration = CredentialType.objects.get(type= CredentialType.CLOUDSTACK)

        return Credential.get_credentials(environment= environment, integration= integration)

    @classmethod
    def get_vm_credentials(self, environment):
        return Credential.get_credentials(environment= environment, integration= CredentialType.objects.get(type= CredentialType.VM))

    @classmethod
    def get_mysql_credentials(self, environment):
        return Credential.get_credentials(environment= environment, integration= CredentialType.objects.get(type= CredentialType.MYSQL))

    @classmethod
    def auth(self, environment):
        LOG.info("Conecting with cloudstack...")
        credentials = self.get_credentials(environment= environment)
        return CloudStackClient(credentials.endpoint, credentials.token, credentials.secret)

    @classmethod
    @transaction.commit_on_success
    def destroy_instance(self, database, *args, **kwargs):

        LOG.warning("Deleting the host on cloud portal...")

        if database.is_in_quarantine:
            super(Database, database).delete(*args, **kwargs)  # Call the "real" delete() method.

            plan = database.databaseinfra.plan
            environment = database.databaseinfra.environment

            hosts = database.databaseinfra.instances.all()
            posic = 0
            for hostobject in hosts:
                posic += 1
                host = hostobject.hostname
                host_attr = HostAttr.objects.filter(host= host)[0]
            
                LOG.info("Remove all database files")
                self.run_script(host, "/opt/dbaas/scripts/dbaas_deletedatabasefiles.sh")
            
            
                LOG.info("Destroying storage (environment:%s, plan: %s, host:%s)!" % (environment, plan, host))
                StorageManager.destroy_disk(environment=environment, plan=plan, host=host)
            
            
                project_id = self.get_credentials(environment= environment).project

                api = self.auth(environment= environment)
                
                self.remove_secondary_ips(api, database.databaseinfra)
                
                request = { 'projectid': '%s' % (project_id),
                            'id': '%s' % (host_attr.vm_id)
                          }
                response = api.destroyVirtualMachine('GET',request)
            
                try:
                    if 'jobid' in response:
                        LOG.warning("VirtualMachine destroyed!")

                        flipper = FlipperProvider()
                        flipper.destroy_flipper_dependencies(masterpairname=database.databaseinfra.name, environment=environment)

                        instance = Instance.objects.get(hostname=host)
                        
                        if posic == len(hosts):
                            databaseinfra = DatabaseInfra.objects.get(instances=instance)
                            databaseinfra.delete()
                            LOG.info("DatabaseInfra destroyed!")
                        
                        instance.delete()
                        LOG.info("Instance destroyed!")
                        host_attr.delete()
                        LOG.info("Host custom cloudstack attrs destroyed!")
                        host.delete()
                        LOG.info("Host destroyed!")
                        paramiko.HostKeys().clear()
                        LOG.info("Removing key from known hosts!")
                        LOG.info("Finished!")
                except Exception, e:
                    LOG.warning("We could not destroy the VirtualMachine.  %s :(" % e)
        else:
            LOG.warning("Putting database %s in quarantine" % database.name)
            database.is_in_quarantine=True
            database.save()
            if database.credentials.exists():
                for credential in database.credentials.all():
                    new_password = make_db_random_password()
                    new_credential = targetdbCredential.objects.get(pk=credential.id)
                    new_credential.password = new_password
                    new_credential.save()

                    instance = factory_for(database.databaseinfra)
                    instance.update_user(new_credential)

    @classmethod
    def run_script(self, host, command):
        host_attr = HostAttr.objects.filter(host= host)[0]

        username = host_attr.vm_user
        password = host_attr.vm_password
        
        LOG.info("Running script [%s] on host %s" % (command, host))
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host.address, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        
        log_stdout = stdout.readlines()
        log_stderr = stderr.readlines()
        cod_ret_start = stdout.channel.recv_exit_status()
        
        LOG.info("Script return code: %s, stdout: %s, stderr %s" % (cod_ret_start, log_stdout, log_stderr))
        return cod_ret_start

    @classmethod
    def check_ssh(self, host, retries=6, initial_wait=30, interval=40):
        host_attr = HostAttr.objects.filter(host= host)[0]

        username = host_attr.vm_user
        password = host_attr.vm_password
        ssh = paramiko.SSHClient()
        port=22
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        LOG.info("Waiting %s seconds to check %s ssh connection..." % (initial_wait, host.address))
        sleep(initial_wait)

        for x in range(retries):
            try:
                LOG.info("Login attempt number %i on %s " % (x+1,host.address))
                ssh.connect(host.address, port=port, 
                                    username=username, password=password, 
                                    timeout= None, allow_agent= True, 
                                    look_for_keys= True, compress= False
                                    )
                return True
            except (paramiko.ssh_exception.BadHostKeyException, 
                        paramiko.ssh_exception.AuthenticationException, 
                        paramiko.ssh_exception.SSHException, socket.error) as e:
                if x == retries-1:
                    LOG.error("Maximum number of login attempts : %s ." % (e))
                    return None 
                LOG.warning("We caught an exception: %s ." % (e))
                LOG.info("Wating %i seconds to try again..." % ( interval + 30))
                sleep(interval)
                sleep(30)
            finally:
                ssh.close()

    @classmethod
    @transaction.commit_on_success
    def create_instance(self, plan, environment, name):
        if plan.is_ha:
            return self.create_instance_cluster(plan, environment, name)
        else:
            return self.create_instance_single(plan, environment, name)

    @classmethod
    @transaction.commit_on_success
    def create_instance_cluster(self, plan, environment, name):
    
        LOG.info("Provisioning new host on cloud portal with options %s %s..." % (plan, environment))
        api = self.auth(environment= environment)
        planattr = PlanAttr.objects.get(plan=plan)
        project_id = self.get_credentials(environment= environment).project
        names = self.gen_infra_name(name, 2)
        infraname = names["infra"]
        
        databaseinfra = self.build_databaseinfra(infraname= infraname, plan= plan, environment= environment)

        instances = []

        for vmname in names["vms"]:
            instance = self.create_vm(api, planattr, project_id, infraname, vmname, plan, environment, True, databaseinfra)

            if instance==None:
                for i in instances:

                    LOG.warning("Destroying cloudstack cluster instance!")
                    self.destroy_vm(environment= environment, instance=i)
                    i.hostname.delete()

                databaseinfra.delete()
                return None
            else:
                instances.append(instance)

        databasesinfraattr = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra)
        if databasesinfraattr[0].is_write:
            write_ip = databasesinfraattr[0].ip
            read_ip = databasesinfraattr[1].ip
        else:
            write_ip = databasesinfraattr[1].ip
            read_ip = databasesinfraattr[0].ip
        contextdict = {
            'EXPORTPATH': None,
            'SERVERID': None,
            'DBPASSWORD': self.get_mysql_credentials(environment=environment).password,
            'IPMASTER': None,
            'IPWRITE': write_ip,
            'IPREAD': read_ip,
            'MASTERPAIRNAME': infraname,
            'HOST01': instances[0].hostname,
            'HOST02': instances[1].hostname,
            'INSTANCE01': instances[0],
            'INSTANCE02': instances[1],
            'SECOND_SCRIPT_FILE': '/opt/dbaas/scripts/dbaas_second_script.sh',
        }

        try:
            self.build_dependencies(contextdict=contextdict, host=contextdict['HOST01'], serverid=1, master=contextdict['HOST02'], 
                                         environment=environment, plan=plan, databaseinfra=databaseinfra, api=api)

            self.build_dependencies(contextdict=contextdict, host=contextdict['HOST02'], serverid=2, master=contextdict['HOST01'], 
                                         environment=environment, plan=plan, databaseinfra=databaseinfra, api=api)
            
            if self.run_script(contextdict['HOST01'], contextdict['SECOND_SCRIPT_FILE'])==0:
                if self.run_script(contextdict['HOST02'], contextdict['SECOND_SCRIPT_FILE'])==0:
                    pass
                else:
                    raise Exception, "We could not run the script on host 2"
            else:
                raise Exception, "We could not run the script on host 1"
        except Exception, e:
            for instance in instances:
                LOG.warning("We could not deploy your cluster because: %s" % e)

                LOG.info("Remove all database files")
                self.run_script(instance.hostname, "/opt/dbaas/scripts/dbaas_deletedatabasefiles.sh")
                StorageManager.destroy_disk(environment= environment, plan= plan, host= instance.hostname)
                self.remove_secondary_ips(api, databaseinfra)
                api.destroyVirtualMachine('POST',{'id': "%s" % (instance.hostname.cs_host_attributes.all()[0].vm_id)})
                instance.hostname.delete()            
                flipper = FlipperProvider()
                flipper.destroy_flipper_dependencies(masterpairname= databaseinfra.name, environment= environment)
            databaseinfra.delete()
            return None
        
        return databaseinfra

    @classmethod
    def destroy_vm(self, environment, instance):
        project_id = self.get_credentials(environment= environment).project

        api = self.auth(environment= environment)
        
        self.remove_secondary_ips(api, instance.databaseinfra)
        
        request = { 'projectid': '%s' % (project_id),
                              'id': '%s' % (instance.hostname.cs_host_attributes.all()[0].vm_id)
                            }
        api.destroyVirtualMachine('GET',request)


    @classmethod
    def build_user_data(self, contextdict, plan):
        planattr = PlanAttr.objects.get(plan=plan)
        
        LOG.info(str(contextdict))

        context = Context(contextdict)
        
        template = Template(planattr.userdata)
        return template.render(context)

    @classmethod
    def build_nfsaas(self, environment, plan, host):
        return StorageManager.create_disk(environment=environment, plan=plan, host=host)

    @classmethod
    def build_flipper(self, contextdict, environment):
        flipper = FlipperProvider()
        flipper.create_flipper_dependencies(masterpairname= contextdict['MASTERPAIRNAME'], 
                                                                readip= contextdict['IPREAD'], 
                                                                writeip= contextdict['IPWRITE'], 
                                                                hostname1= contextdict['HOST01'].address, 
                                                                hostname2= contextdict['HOST02'].address, 
                                                                environment= environment)

    @classmethod
    def update_userdata(self, host, api, plan, contextdict):
        host_attr = HostAttr.objects.filter(host= host)[0]
        request = { 'id': host_attr.vm_id, 
                          'userdata': b64encode(self.build_user_data(contextdict, plan))
                        }
        api.updateVirtualMachine('POST', request)
            
        self.run_script(host, "/opt/dbaas/scripts/dbaas_userdata_script.sh")
        LOG.info("Host %s is ready!" % (host.address))

    @classmethod
    @transaction.commit_on_success
    def build_dependencies(self, contextdict, host, serverid, master, environment, plan, databaseinfra, api):
        try:
            disk = self.build_nfsaas(environment= environment, plan= plan, host= host)

            contextdict['EXPORTPATH'] = disk['path']
            contextdict['SERVERID'] = serverid
            contextdict['IPMASTER'] = master

            self.update_userdata(host= host, api= api, plan= plan, contextdict= contextdict)

            if serverid==1:
                self.build_flipper(contextdict= contextdict, environment= environment)
            
            contextdict['INSTANCE01'].databaseinfra = databaseinfra
            contextdict['INSTANCE01'].save()

            contextdict['INSTANCE02'].databaseinfra = databaseinfra
            contextdict['INSTANCE02'].save()

            LOG.info("Instance created!")
            
            return databaseinfra
        except Exception, e:
            print e

    @classmethod
    @transaction.commit_on_success
    def create_instance_single(self, plan, environment, name):
    
        LOG.info("Provisioning new host on cloud portal with options %s %s..." % (plan, environment))
        api = self.auth(environment= environment)
        planattr = PlanAttr.objects.get(plan=plan)
        project_id = self.get_credentials(environment= environment).project
        names = self.gen_infra_name(name, 1)
        infraname = names["infra"]
        vmname = names["vms"][0]
        
        databaseinfra =  self.build_databaseinfra(infraname= infraname, plan= plan, environment= environment)
        
        instance = self.create_vm(api, planattr, project_id, infraname, vmname, plan, environment, False, databaseinfra)
        if instance is None:
            databaseinfra.delete()
            return None
        
        
        databaseinfra.endpoint = instance.address + ":%i" %(instance.port)
        databaseinfra.endpoint_dns = instance.dns + ":%i" %(instance.port)
        databaseinfra.save()
        instance.databaseinfra = databaseinfra
        instance.save()
        LOG.info("Instance created!")
        
        return databaseinfra

    @classmethod
    def build_databaseinfra(self, infraname, plan, environment):
        mysql_credentials = self.get_mysql_credentials(environment=environment)
        databaseinfra = DatabaseInfra()
        databaseinfra.name = infraname
        databaseinfra.user  = mysql_credentials.user
        databaseinfra.password = mysql_credentials.password
        databaseinfra.engine = plan.engine_type.engines.all()[0]
        databaseinfra.plan = plan
        databaseinfra.environment = environment
        databaseinfra.capacity = 1
        databaseinfra.per_database_size_mbytes=0
        databaseinfra.save()
        LOG.info("DatabaseInfra created!")
        return databaseinfra

    @classmethod
    def reserve_ip(self, project_id, host_attr, api):
        request = {'projectid': '%s' % (project_id), 'id':'%s' % (host_attr.vm_id) }
        response = api.listVirtualMachines('GET',request)
        nicid = response['virtualmachine'][0]['nic'][0]['id']
        api.addIpToNic('GET', {'nicid': nicid})

        sleep(20)    
        request['virtualmachineid'] = host_attr.vm_id
        response = api.listNics('GET',request)
        secondary_ip = response['nic'][0]['secondaryip'][0]['ipaddress']
        cs_ip_id = response['nic'][0]['secondaryip'][0]['id']
        LOG.info('Secondary ip %s do host %s' % (secondary_ip, host_attr.host))
        return secondary_ip, cs_ip_id
        
    @classmethod
    @transaction.commit_on_success    
    def create_vm(self, api, planattr, project_id, infraname, vmname, plan, environment, cluster, databaseinfra):

        request = { 'serviceofferingid': planattr.serviceofferingid, 
                          'templateid': planattr.templateid, 
                          'zoneid': planattr.zoneid,
                          'networkids': planattr.networkid,
                          'projectid': project_id,
                          'name': vmname,
                        }

        response = api.deployVirtualMachine('POST',request)
        
        LOG.info(" CloudStack response %s" % (response))

        try:
            if 'jobid' in response:
                LOG.info("VirtualMachine created!")
                request = {'projectid': '%s' % (project_id), 'id':'%s' % (response['id']) }
                
                host_attr = HostAttr()
                host_attr.vm_id = response['id']

                response = api.listVirtualMachines('GET',request)
                host = Host()
                host.address = response['virtualmachine'][0]['nic'][0]['ipaddress']
                host.hostname = self.add_dns_record(databaseinfra=databaseinfra, name=vmname, ip=host.address, type=DNSAPI_HOST)
                host.cloud_portal_host = True
                host.save()

                LOG.info("Host created!")
                
                vm_credentials = self.get_vm_credentials(environment=environment)
                host_attr.vm_user = vm_credentials.user
                host_attr.vm_password = vm_credentials.password
                host_attr.host = host
                host_attr.save()
                LOG.info("Host attrs custom attributes created!")

                instance = Instance()
                instance.address = host.address
                instance.dns = self.add_dns_record(databaseinfra=databaseinfra, name=vmname, ip=instance.address, type=DNSAPI_INSTANCE)
                instance.port = 3306
                instance.is_active = True
                instance.is_arbiter = False
                instance.hostname = host
                
            else:
                return None

            ssh_ok = self.check_ssh(host)
            
            if  ssh_ok:
                if cluster:
                    databaseinfraattr = DatabaseInfraAttr()
                    total = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra).count()
                    if total == 0:
                        databaseinfraattr.is_write = True
                        dnsname = databaseinfra.name
                        
                    else:
                        databaseinfraattr.is_write = False
                        dnsname = databaseinfra.name + '-r'                 
                    databaseinfraattr.ip , databaseinfraattr.cs_ip_id= self.reserve_ip(project_id= project_id, host_attr= host_attr, api= api)
                    databaseinfraattr.databaseinfra = databaseinfra
                    databaseinfraattr.dns = self.add_dns_record(databaseinfra=databaseinfra, name=dnsname, ip=databaseinfraattr.ip, type=DNSAPI_FLIPPER)
                    databaseinfraattr.save()
                    if total == 0:
                        databaseinfra.endpoint = databaseinfraattr.ip + ":%i" %(3306)
                        databaseinfra.endpoint_dns = databaseinfraattr.dns + ":%i" %(3306)
                        databaseinfra.save()
                else:
                    disk = self.build_nfsaas(environment=environment, plan=plan, host=host)
                    self.update_userdata(host= host, api= api, plan= plan, contextdict={"EXPORTPATH": disk['path']})
                return instance
            else:
                raise Exception, "Maximum number of login attempts!"

        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)

            if 'virtualmachine' in response:
                if 'databaseinfraattr' in locals() and databaseinfraattr:
                    self.remove_secondary_ips(api, databaseinfraattr.databaseinfra)
                vm_id = response['virtualmachine'][0]['id']
                LOG.info("Destroying VirtualMachine %s on cloudstack." % (vm_id))
                api.destroyVirtualMachine('POST',{'id': "%s" % (vm_id)})
                LOG.info("VirtualMachine destroyed!")
                if 'disk' in locals() and disk:
                    LOG.info("Destroying storage...")
                    StorageManager.destroy_disk(environment= environment, plan= plan, host= host)
                    LOG.info("Storage destroyed!")
                self.del_dns_record(databaseinfra)
            else:
               LOG.warning("Something ocurred on cloudstack: %i, %s" % (response['errorcode'], response['errortext']))
            
            return None

    @classmethod
    def gen_infra_name(self, name, qt):
        import time
        import re
        
        stamp = str(time.time()).replace(".","")
        name = re.compile("[^\w']|_").sub("", name.lower())
        name = name[:10]
        names = {"infra": name + stamp, "vms":[]}

        for x in range(qt):
            names['vms'].append(name + "-0%i-" % (x+1)+ stamp)

        return names

    @classmethod
    @transaction.commit_on_success 
    def remove_secondary_ips(self, api, databaseinfra):
        databaseinfraattrs = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra)
        for databaseinfraattr in databaseinfraattrs:
            LOG.info("Removing secondary ip (id: %s)" % (databaseinfraattr.cs_ip_id))
            api.removeIpFromNic('POST',{'id': databaseinfraattr.cs_ip_id})
            databaseinfraattr.delete()
