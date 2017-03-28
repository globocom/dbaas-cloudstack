from django.contrib.auth.models import User


def make_db_random_password():
    return User.objects.make_random_password()


def get_cs_credential(environment):
    from dbaas_credentials.models import Credential
    from dbaas_credentials.models import CredentialType

    return Credential.objects.filter(
        integration_type__type=CredentialType.CLOUDSTACK,
        environments=environment)[0]
    return
