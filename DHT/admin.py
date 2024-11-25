from django.contrib import admin
from . import models

class Dht11Admin(admin.ModelAdmin):
    list_display = ('temp', 'hum', 'dt') 
    search_fields = ('temp', 'hum')

admin.site.register(models.Dht11, Dht11Admin)
