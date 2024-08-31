from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProfileUser

@receiver(post_save, sender=User)
def create_profile_user(sender, instance, created, **kwargs):
    
    if created:
        profile_user = ProfileUser.objects.create(user=instance)
        profile_user.tags = ['home']
        profile_user.save()