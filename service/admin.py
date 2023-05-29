from django.contrib import admin
from .models import (
    Saloon, Service, Category, Master, Client, Appointment,
    Feedback
    )


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


class ServiceInLine(admin.TabularInline):
    model = Service
    autocomplete_fields = ('masters',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title',)
    inlines = (ServiceInLine,)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'saloon', 'time_create',)
    readonly_fields = ('time_create',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'phonenumber', 'time_create', 'user_id')
    readonly_fields = ('time_create',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ('client',)
    readonly_fields = ('time_create',)
    list_display = (
        'client', 'master', 'service',
        'appointment_date', 'appointment_time', 'time_create'
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('client', 'appointment', 'feedback_text')
    search_fields = ('client', 'feedback_text')
    list_filter = ('appointment',)
    ordering = ('appointment', 'client')
