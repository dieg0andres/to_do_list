from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProfileUser, Tag

@receiver(post_save, sender=User)
def create_profile_user(sender, instance, created, **kwargs):
    
    if created:
        profile_user = ProfileUser.objects.create(user=instance)
        
        tag =Tag.objects.create(name='Home', shared=False)
        tag.users.add(instance)
        profile_user.selected_tag_unique_str = tag.unique_str
        profile_user.save()