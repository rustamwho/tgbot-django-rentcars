from django.contrib import admin, auth
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django_celery_beat.models import (PeriodicTask, IntervalSchedule,
                                       CrontabSchedule, SolarSchedule,
                                       ClockedSchedule)

from dtb.settings import DEBUG

from tgbot.models import User
from tgbot.forms import BroadcastForm

from tgbot.tasks import broadcast_message
from tgbot.handlers.broadcast_message.utils import _send_message

from rentcars.models import PersonalData


admin.site.site_header = 'Администрирование Elit Transfer'
admin.site.unregister(auth.models.Group)
# Delete django celery beat from admin panel
for dcb_model in (IntervalSchedule, PeriodicTask, CrontabSchedule,
                  SolarSchedule, ClockedSchedule):
    admin.site.unregister(dcb_model)


class QuestionInline(admin.StackedInline):
    model = PersonalData
    extra = 5
    show_change_link = True


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'username', 'first_name', 'last_name', 'personal_data',
        'language_code', 'deep_link',
        'created_at', 'updated_at', "is_blocked_bot",
    ]
    list_filter = ["is_blocked_bot", "is_moderator"]
    search_fields = ('username', 'user_id')
    inlines = (QuestionInline,)

    actions = ['broadcast']

    def broadcast(self, request, queryset):
        """
        Select users via check mark in django-admin panel,
        then select "Broadcast" to send message.
        """
        user_ids = queryset.values_list('user_id',
                                        flat=True).distinct().iterator()
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            if DEBUG:  # for test / debug purposes - run in same thread
                for user_id in user_ids:
                    _send_message(
                        user_id=user_id,
                        text=broadcast_message_text,
                    )
                self.message_user(request,
                                  f"Just broadcasted to {len(queryset)} users")
            else:
                broadcast_message.delay(text=broadcast_message_text,
                                        user_ids=list(user_ids))
                self.message_user(
                    request,
                    f"Broadcasting of {len(queryset)} "
                    f"messages has been started")

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastForm(initial={'_selected_action': user_ids})
            return render(
                request, "admin/broadcast_message.html",
                {'form': form, 'title': u'Broadcast message'}
            )
