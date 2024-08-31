from django.db import models
from django.contrib.auth.models import User


class DoItem(models.Model):
    title = models.CharField(max_length=288)
    description = models.TextField()
    complete = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='do_items')
    tag = models.CharField(max_length=50, default='home')
    
    def __str__(self):
        return self.title
    

class ProfileUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tag_selected = models.CharField(max_length=50, default='home')
    tags = models.JSONField(default=list)


    def __str__(self):
        return self.user.email
