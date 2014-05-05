# -*- coding: utf-8 -*-
from client import CloudStackClient
from django.db import transaction
from physical.models import DatabaseInfra, Instance, Host
from util import make_db_random_password
from drivers import factory_for
from .models import PlanAttr, HostAttr, DatabaseInfraAttr
from base64 import b64encode
import logging
from integrations.storage.manager import StorageManager
from django.template import Context, Template
from time import sleep
import paramiko
import socket
import MySQLdb


LOG = logging.getLogger(__name__)

class CloudStackProvider(object):

    @classmethod
    def get_credentials(self, environment):
        LOG.info("Getting credentials...")
        from dbaas_credentials.credential import Credential
        from dbaas_credentials.models import CredentialType
        integration = CredentialType.objects.get(type= CredentialType.CLOUDSTACK)

        return Credential.get_credentials(environment= environment, integration= integration)

    @classmethod
    def auth(self, environment):
        LOG.info("Conecting with cloudstack...")
        credentials = self.get_credentials(environment= environment)
        return CloudStackClient(credentials.endpoint, credentials.token, credentials.secret)

    @classmethod
    @transaction.commit_on_success
    def destroy_instance(self, database, *args, **kwargs):
        from logical.models import Credential, Database

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
                request = { 'projectid': '%s' % (project_id),
                            'id': '%s' % (host_attr.vm_id)
                          }
                response = api.destroyVirtualMachine('GET',request)
            
                try:
                    if response['jobid']:
                        LOG.warning("VirtualMachine destroyed!")

                        instance = Instance.objects.get(hostname=host)
                        
                        if posic == len(hosts):
                            databaseinfra = DatabaseInfra.objects.get(instances=instance)
                            databaseinfra.delete()
                            LOG.info("DatabaseInfra destroyed!")
                        
                        instance.delete
                        LOG.info("Instance destroyed!")
                        host_attr.delete()
                        LOG.info("Host custom cloudstack attrs destroyed!")
                        host.delete()
                        LOG.info("Host destroyed!")
                        paramiko.HostKeys().clear()
                        LOG.info("Removing key from known hosts!")
                        LOG.info("Finished!")
                except (KeyError, LookupError):
                    LOG.warning("We could not destroy the VirtualMachine. :(")
        else:
            LOG.warning("Putting database %s in quarantine" % database.name)
            database.is_in_quarantine=True
            database.save()
            if database.credentials.exists():
                for credential in database.credentials.all():
                    new_password = make_db_random_password()
                    new_credential = Credential.objects.get(pk=credential.id)
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
        client.connect(host.hostname, username=username, password=password)
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

        LOG.info("Waiting %s seconds to check %s ssh connection..." % (initial_wait, host.hostname))
        sleep(initial_wait)

        for x in range(retries):
            try:
                LOG.info("Login attempt number %i on %s " % (x+1,host.hostname))
                ssh.connect(host.hostname, port=port, 
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
        vmname = names["vms"][0]
        
        
        #response = api.listVirtualMachines('GET',request)
        #print response
        
        databaseinfra = DatabaseInfra()
        databaseinfra.name = infraname
        databaseinfra.user  = 'root'
        databaseinfra.password = 'root'
        databaseinfra.engine = plan.engine_type.engines.all()[0]
        databaseinfra.plan = plan
        databaseinfra.environment = environment
        databaseinfra.capacity = 1
        databaseinfra.per_database_size_mbytes=0
        #databaseinfra.endpoint = instance1.address + ":%i" %(instance1.port)
        databaseinfra.save()
        LOG.info("DatabaseInfra created!")

        instance1 = self.create_vm(api, planattr, project_id, infraname, names["vms"][0], plan, environment, True, databaseinfra)
        instance2 = self.create_vm(api, planattr, project_id, infraname, names["vms"][1], plan, environment, True, databaseinfra)        
        if instance1 is None or instance2 is None:
            databaseinfra.delete()
            return None
        databasesinfraattr = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra)
        databasesinfraattr[0].is_write = True
        databasesinfraattr[0].save()
        writeip = databasesinfraattr[0].ip
        readip = databasesinfraattr[1].ip
        masterpairname = name[0:20]
        second_script = '/opt/dbaas/scripts/dbaas_second_script.sh'
        contextdict = {
            'EXPORTPATH': None,
            'SERVERID': None,
            'DBPASSWORD': 'root',
            'IPMASTER': None,
            'IPWRITE': writeip,
            'HOST01': instance1.hostname,
            'HOST02': instance2.hostname,
            'MASTERPAIRNAME': masterpairname,
            'SECOND_SCRIPT_FILE': second_script,
        }
        def run_scripts_vms(contextdict, host, serverid, master):
            #host = intance.hostname
            host_attr = HostAttr.objects.filter(host= host)[0]
            disk = StorageManager.create_disk(environment=environment, plan=plan, host=host)
            contextdict['EXPORTPATH'] = disk['path']
            contextdict['SERVERID'] = serverid
            contextdict['IPMASTER'] = master
            
            LOG.info(str(contextdict))

            context = Context(contextdict)
            
            template = Template(planattr.userdata)
            userdata = template.render(context)
                            
            request = {'id': host_attr.vm_id, 'userdata': b64encode(userdata)}
            response = api.updateVirtualMachine('POST', request)
                
            self.run_script(host, "/opt/dbaas/scripts/dbaas_userdata_script.sh")

            LOG.info("Host %s is ready!" % (host.hostname))
        
        
        ##### cadastro metadados flipper
        
        flipper_conn = MySQLdb.connect(host='dev.mysql.globoi.com', port=3306,
                                     user='flipper', passwd='flipit!',
                                     db='flipper_metadata')
        flipper_cursor = flipper_conn.cursor()
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'broadcast', '10.25.12.255')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'mysql_password', 'flipit!')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'mysql_user', 'flipper')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'netmask', '255.255.255.0')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'quiesce_strategy', 'KillAll')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'read_ip', readip)
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'send_arp_command', '/sbin/arping -I $sendarp_interface -c 5 -U -A $sendarp_ip')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'ssh_user', 'flipper')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'use_sudo', '1')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO masterpair (masterpair, name, value) values ('%s', '%s', '%s')" % (masterpairname, 'write_ip', writeip)
        flipper_cursor.execute(sql_insert)
        
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'interface', 'eth2')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'ip', instance1.hostname.hostname)
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'read_interface', 'eth2:98')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance1.hostname.hostname, 'write_interface', 'eth2:99')
        flipper_cursor.execute(sql_insert)

        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'interface', 'eth2')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'ip', instance2.hostname.hostname)
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'read_interface', 'eth2:98')
        flipper_cursor.execute(sql_insert)
        sql_insert = "INSERT INTO node (masterpair, node, name, value) values ('%s', '%s', '%s', '%s')" % (masterpairname, instance2.hostname.hostname, 'write_interface', 'eth2:99')
        flipper_cursor.execute(sql_insert)
        
        flipper_cursor.execute("commit")

        
        run_scripts_vms(contextdict, instance1.hostname, 1, instance2.address )
        run_scripts_vms(contextdict, instance2.hostname, 2, instance1.address )
        self.run_script(instance1.hostname, second_script)
        self.run_script(instance2.hostname, second_script)
        

        #databaseinfra.endpoint = writeip + ":%i" %(3306)
        databaseinfra.endpoint = instance1.hostname.hostname + ":%i" %(3306)
        databaseinfra.save()
        
        instance1.databaseinfra = databaseinfra
        instance1.save()

        instance2.databaseinfra = databaseinfra
        instance2.save()

        LOG.info("Instance created!")
        
        return databaseinfra

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
        
        instance = self.create_vm(api, planattr, project_id, infraname, vmname, plan, environment, False, None)
        if instance is None:
            return None
        
        databaseinfra = DatabaseInfra()
        databaseinfra.name = infraname
        databaseinfra.user  = 'root'
        databaseinfra.password = 'root'
        databaseinfra.engine = plan.engine_type.engines.all()[0]
        databaseinfra.plan = plan
        databaseinfra.environment = environment
        databaseinfra.capacity = 1
        databaseinfra.per_database_size_mbytes=0
        databaseinfra.endpoint = instance.address + ":%i" %(instance.port)
        databaseinfra.save()
        LOG.info("DatabaseInfra created!")
        
        instance.databaseinfra = databaseinfra
        instance.save()
        LOG.info("Instance created!")
        
        return databaseinfra
            
        

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
                host.hostname = response['virtualmachine'][0]['nic'][0]['ipaddress']
                host.cloud_portal_host = True
                host.save()
                LOG.info("Host created!")
                    
                host_attr.vm_user = 'root'
                host_attr.vm_password = 'ChangeMe'
                host_attr.host = host
                host_attr.save()
                LOG.info("Host attrs custom attributes created!")

                instance = Instance()
                instance.address = host.hostname
                instance.port = 3306
                instance.is_active = True
                instance.is_arbiter = False
                instance.hostname = host
            
            else:
                return None

            ssh_ok = self.check_ssh(host)
            
            if  ssh_ok:

                if cluster:
                    request = {'projectid': '%s' % (project_id), 'id':'%s' % (host_attr.vm_id) }
                    response = api.listVirtualMachines('GET',request)
                    nicid = response['virtualmachine'][0]['nic'][0]['id']
                    api.addIpToNic('GET', {'nicid': nicid})
                    
                    sleep(20)    
                    request['virtualmachineid'] = host_attr.vm_id
                    response = api.listNics('GET',request)
                    secondary_ip = response['nic'][0]['secondaryip'][0]['ipaddress']
                    LOG.info('Secondary ip %s do host %s' % (secondary_ip, host_attr.host))
                    
                    databaseinfraattr = DatabaseInfraAttr()
                    databaseinfraattr.ip = secondary_ip
                    databaseinfraattr.databaseinfra = databaseinfra
                    databaseinfraattr.save()
                
                else:

                    disk = StorageManager.create_disk(environment=environment, plan=plan, host=host)
                    context = Context({"EXPORTPATH": disk['path']})
            
                    template = Template(planattr.userdata)
                    userdata = template.render(context)
                            
                    request = {'id': host_attr.vm_id, 'userdata': b64encode(userdata)}
                    response = api.updateVirtualMachine('POST', request)
                
                    self.run_script(host, "/opt/dbaas/scripts/dbaas_userdata_script.sh")

                    LOG.info("Host %s is ready!" % (host.hostname))
                
                return instance
            
            else:
                
                raise Exception, "Maximum number of login attempts!"

        except Exception, e:
            LOG.warning("We could not create the VirtualMachine because %s" % e)

            if 'virtualmachine' in response:
                vm_id = response['virtualmachine'][0]['id']
                LOG.info("Destroying VirtualMachine %s on cloudstack." % (vm_id))
                api.destroyVirtualMachine('POST',{'id': "%s" % (vm_id)})
                LOG.info("VirtualMachine destroyed!")
                if 'disk' in locals():
                    if disk:
                        LOG.info("Destroying storage...")
                        StorageManager.destroy_disk(environment= environment, plan= plan, host= host)
                        LOG.info("Storage destroyed!")
            else:
               LOG.warning("Something ocurred on cloudstack: %i, %s" % (response['errorcode'], response['errortext']))
            
            return None

    @classmethod
    def gen_infra_name(self, name, qt):
        import time
        import re

        stamp = str(time.time()).replace(".","")
        name = re.compile("[^\w']|_").sub("", name.lower())
        names = {"infra": name + stamp, "vms":[]}

        for x in range(qt):
            names['vms'].append(name + "-00%i-" % (x+1)+ stamp)

        return names