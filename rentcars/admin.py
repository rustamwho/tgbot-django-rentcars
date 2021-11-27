from django.contrib import admin

from rentcars.models import (PersonalData, Contract, PhotoCarContract, Car,
                             PhotoCar, Fine)


class PhotoCarContractInline(admin.TabularInline):
    fk_name = 'contract'
    model = PhotoCarContract


@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    list_display = (
        'last_name', 'first_name', 'middle_name', 'gender', 'email',
        'birthday', 'phone_number', 'passport_serial', 'passport_number',
        'passport_date_of_issue', 'passport_issued_by', 'address_registration',
        'close_person_name', 'created_at', 'updated_at')
    search_fields = ('last_name', 'first_name', 'middle_name')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'file', 'car', 'created_at',
                    'approved_at', 'closed_at')
    search_fields = ('user__username', 'user__personal_data__last_name',
                     'user__personal_data__first_name',
                     'user__personal_data__middle_name')
    inlines = [PhotoCarContractInline]

    def is_active(self, obj):
        return obj.is_active

    is_active.boolean = True


class PhotoCarInline(admin.TabularInline):
    fk_name = 'car'
    model = PhotoCar


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'is_busy', 'vin', 'model',
                    'type', 'category', 'year_manufacture', 'color', 'power',
                    'sts_serial', 'sts_number')
    search_fields = ('license_plate', 'model', 'owner__last_name',
                     'owner__first_name', 'owner__middle_name')
    inlines = [PhotoCarInline]

    def is_busy(self, obj):
        return obj.is_busy

    is_busy.boolean = True


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('car', 'datetime', 'amount', 'is_paid', 'user', 'contract')
    search_fields = ('car__license_plate', 'user__username',
                     'user__personal_data__last_name',
                     'user__personal_data__first_name',
                     'user__personal_data__middle_name')
    list_filter = ('is_paid',)
