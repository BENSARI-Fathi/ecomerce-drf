from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save


@receiver(pre_save, sender=User)
def update_user(sender, instance, **kwargs):
    user = instance
    if user.email != '':
        user.username = user.email


"""
    when we create a signal-function in a custom file we must import 
    the funtion in models.py to use it or 
    we must create a function named ready in apps.py and import the app 
    name in settings.py as <appname>.apps.<appname>Config 
"""
