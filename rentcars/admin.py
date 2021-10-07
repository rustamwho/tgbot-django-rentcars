from django.contrib import admin

from rentcars.models import PersonalData


@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'middle_name', 'gender', 'email',
        'birthday', 'phone_number', 'passport_serial', 'passport_number',
        'passport_date_of_issue', 'passport_issued_by', 'address_registration',
        'close_person_name')
