from django.contrib import admin
from . import models
@admin.register(models.Farm)
class FarmAdmin(admin.ModelAdmin):
    pass
@admin.register(models.Gcg)
class GcgAdmin(admin.ModelAdmin):
    pass
@admin.register(models.ControlGroup)
class ControlGroupAdmin(admin.ModelAdmin):
    pass
@admin.register(models.ControlOpenOption)
class ControlOpenOptionAdmin(admin.ModelAdmin):
    pass
@admin.register(models.ControlOpenGroup)
class ControlOpenGroupAdmin(admin.ModelAdmin):
    pass
@admin.register(models.SensorInfoOrValue)
class SensorInfoOrValueAdmin(admin.ModelAdmin):
    pass
@admin.register(models.WeatherInfo)
class WeatherInfoAdmin(admin.ModelAdmin):
    pass
@admin.register(models.TestModel)
class TestModelAdmin(admin.ModelAdmin):
    pass
# Register your models here.
