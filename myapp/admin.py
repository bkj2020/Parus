from django.contrib import admin
from .models import (Country, Hot_guest, Hot_room, Hot_book)

# Register your models here.
admin.site.register(Country)

# Define the admin class.
class HotGuestAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name')

# Register the admin class with associated model
admin.site.register(Hot_guest, HotGuestAdmin)
admin.site.register(Hot_room)
admin.site.register(Hot_book)


