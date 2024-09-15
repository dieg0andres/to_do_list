import random
import string
from django.db import models
from django.contrib.auth.models import User




def create_unique_str():
        while True:
            unique_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Tag.objects.filter(unique_str=unique_str).exists():
                return unique_str


class Tag(models.Model):
    print('test')
    name = models.CharField(max_length=50, default='Home')
    shared = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='tags')
    unique_str = models.CharField(max_length=8, default=create_unique_str)

    def __str__(self):
        return self.name


class DoItem(models.Model):
    title = models.CharField(max_length=288)
    description = models.TextField()
    complete = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='do_items')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='do_items')
    
    def __str__(self):
        return self.title
    

class ProfileUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    selected_tag_unique_str = models.CharField(max_length=8)


    def __str__(self):
        return self.user.email



    