from django.contrib import admin
from . import models
@admin.register(models.Farm)
class FarmAdmin(admin.ModelAdmin):
    pass

# Register your models here.
