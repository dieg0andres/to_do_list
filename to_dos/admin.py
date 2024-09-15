from django.contrib import admin
from .models import (
    DoItem, 
    ProfileUser, 
    Tag
)

# Register your models here.
admin.site.register(DoItem)
admin.site.register(ProfileUser)
admin.site.register(Tag)
