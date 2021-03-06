from __future__ import annotations

from typing import Union, Optional, Tuple, Dict

from django.db import models
from django.db.models import QuerySet
from django.utils.timezone import now
from telegram import Update

from dtb.settings import DEBUG
from tgbot.handlers.utils.info import extract_user_data_from_update
from general_utils.models import CreateUpdateTracker, nb, CreateTracker


class User(CreateUpdateTracker):
    user_id = models.IntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8,
                                     help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    def __str__(self):
        user = (f'@{self.username}' if self.username is not None
                else f'{self.user_id}')
        if hasattr(self, 'personal_data'):
            user = (f'{self.personal_data.last_name} '
                    f'{self.personal_data.first_name}')
        return user

    @classmethod
    def get_user_and_created(cls, update: Update,
                             context) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"],
                                                  defaults=data)

        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(
                    context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(
                        data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(
            cls,
            username_or_user_id: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id),
                                   created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"

    def get_active_contract(self):
        """Return active contract with current user."""
        if self.contracts.filter(closed_at__gte=now()).exists():
            return self.contracts.get(closed_at__gte=now())
        return None

    def get_user_all_fines(self, limit: int = None):
        """Return all fines of user"""
        if self.fines.exists():
            return self.fines.all()[:limit] if limit else self.fines.all()
        return None

    def get_user_fines_count(self, is_paid: bool = None):
        """Return count of user's paid or unpaid fines."""
        if is_paid in (True, False):
            return self.fines.filter(is_paid=is_paid).count()
        return self.fines.count()

    def get_user_paid_or_unpaid_fines(self, is_paid: bool):
        """Return paid or unpaid fines."""
        fines = self.fines.filter(is_paid=is_paid)
        if fines.exists():
            return fines
        return None
