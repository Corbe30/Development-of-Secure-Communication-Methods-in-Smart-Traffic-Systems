from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Event)
admin.site.register(models.Car)
admin.site.register(models.Vote)
admin.site.register(models.Block)