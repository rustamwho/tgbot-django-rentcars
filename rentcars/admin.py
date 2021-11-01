from django.contrib import admin

from rentcars.models import (PersonalData, Contract, PhotoCarContract, Car,
                             PhotoCar, Fine)


class PhotoCarContractInline(admin.TabularInline):
    fk_name = 'contract'
    model = PhotoCarContract


@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'middle_name', 'gender', 'email',
        'birthday', 'phone_number', 'passport_serial', 'passport_number',
        'passport_date_of_issue', 'passport_issued_by', 'address_registration',
        'close_person_name', 'created_at', 'updated_at')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'created_at', 'closed_at')
    inlines = [PhotoCarContractInline]


class PhotoCarInline(admin.TabularInline):
    fk_name = 'car'
    model = PhotoCar


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'vin', 'model', 'type', 'category',
                    'year_manufacture', 'color', 'power', 'sts_serial',
                    'sts_number', 'is_busy')
    inlines = [PhotoCarInline]


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('car', 'date', 'amount', 'user', 'contract')
