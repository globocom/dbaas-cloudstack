import sleep
import logging
import paramiko
import socket
from dbaas_credentials.models import Credential, CredentialType
LOG = logging.getLogger(__name__)



class Util(object):

        @classmethod
        def check_nslookup(self, dns_to_check, dns_server, retries= 90, wait= 10):
            import subprocess
            import re

            try:
                for attempt in range(0, retries):
                    LOG.info("Cheking dns... attempt number %i..." % attempt + 1)

                    result = subprocess.Popen("nslookup %s %s" % (dns_to_check, dns_server), stdout=subprocess.PIPE, shell=True)
                    (output, err) = result.communicate()
                    indexes = [i for i, x in enumerate(output.split('\n')) if re.match(r'\W*' + "Address" + r'\W*', x)]

                    LOG.info("Nslookup output: %s" % output)

                    if len(indexes) < 2:
                        LOG.info("%s is available!" % dns_to_check)
                        return True
                    sleep(wait)

                return False
            except Exception, e:
                LOG.warn("We caught an exception %s" % e)
                return None


            @classmethod
            def exec_remote_command(self, server, username, password, command):
                try:
                    LOG.info("Executing command [%s] on remote server %s" % (command, server))
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(server, username= username, password= password)

                    stdin, stdout, stderr = client.exec_command(command)
                    log_stdout = stdout.readlines()
                    log_stderr = stderr.readlines()
                    exit_status = stdout.channel.recv_exit_status()
                    LOG.info("Comand return code: %s, stdout: %s, stderr %s" % (exit_status, log_stdout, log_stderr))

                    return exit_status
                except (paramiko.ssh_exception.SSHException) as e:
                    LOG.warning("We caught an exception: %s ." % (e))
                    return None



            @classmethod
            def check_ssh(self, server, username, password, retries=6, wait=30, interval=40):
                username = username
                password = password
                ssh = paramiko.SSHClient()
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                LOG.info("Waiting %s seconds to check %s ssh connection..." % (wait, server))
                sleep(wait)

                for attempt in range(retries):
                    try:

                        LOG.info("Login attempt number %i on %s " % (attempt+1, server))

                        ssh.connect( server, port=22, username=username, 
                                             password=password, timeout= None, allow_agent= True, 
                                             look_for_keys= True, compress= False)
                        return True

                    except (paramiko.ssh_exception.BadHostKeyException, 
                                paramiko.ssh_exception.AuthenticationException, 
                                paramiko.ssh_exception.SSHException, 
                                socket.error) as e:

                        if attempt == retries-1:
                            LOG.error("Maximum number of login attempts : %s ." % (e))
                            return False

                        LOG.warning("We caught an exception: %s ." % (e))
                        LOG.info("Wating %i seconds to try again..." % ( interval))
                        sleep(interval)

            @classmethod
            def gen_infra_names(self, name, qt):
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
            def get_credentials_for(self, environment, credential_type):
                return Credential.get_credentials(environment= environment, integration= CredentialType.objects.get(type= credential_type))
