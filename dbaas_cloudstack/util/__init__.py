from django.contrib.auth.models import User

def make_db_random_password():
    return User.objects.make_random_password()