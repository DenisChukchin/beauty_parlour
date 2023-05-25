from django.contrib import admin

from .models import Saloon, Service, Category, Master, Client, Appointment


class MasterInLine(admin.TabularInline):
    model = Master


@admin.register(Saloon)
class SaloonAdmin(admin.ModelAdmin):
    search_fields = ('city',)
    list_display = ('title', 'city', 'address', 'phonenumber')
    inlines = (MasterInLine,)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'price',)
    autocomplete_fields = ('masters',)
    raw_id_fields = ('masters',)


class ServiceInLine(admin.TabularInline):
    model = Service
    raw_id_fields = ('masters', 'category',)
    autocomplete_fields = ('masters',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title',)
    inlines = (ServiceInLine,)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'saloon')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'phonenumber',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ('client',)
    list_display = (
        'client', 'master', 'service', 'appointment_date', 'appointment_time'
    )
