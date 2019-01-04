from django.contrib import admin
from . import models
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass
# Register your models here.
@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
# Register your models here.
