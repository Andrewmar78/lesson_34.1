import logging
import os
from datetime import datetime, timedelta
from enum import IntEnum, auto
from typing import NoReturn

from django.core.management import BaseCommand
from pydantic import BaseModel

from backend import settings
from backend.settings import TG_TOKEN
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.fsm.memory_storage import MemoryStorage
from bot.tg.models import Message
from goals.models import Goal, GoalCategory, BoardParticipant

logger = logging.getLogger(__name__)


class NewGoal(BaseModel):
    """Goal base model"""
    cat_id: int | None = None
    goal_title: str | None = None

    @property
    def is_completed(self) -> bool:
        return None not in [self.cat_id, self.goal_title]


class StateEnum(IntEnum):
    """Category selection class"""
    CREATE_CATEGORY_SELECT = auto()
    CHOSEN_CATEGORY = auto()


class Command(BaseCommand):
    """Telegram bot notifications"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.TG_TOKEN)
        self.storage = MemoryStorage()

    @staticmethod
    def _generate_verification_code() -> str:
        """Verification code creation"""
        return os.urandom(12).hex()

    def handle_unverified_user(self, msg: Message, tg_user: TgUser) -> NoReturn:
        """Return verification code to user"""
        code: str = self._generate_verification_code()
        tg_user.verification_code = code
        tg_user.save(update_fields=('verification_code',))
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'[verification code] {tg_user.verification_code}'
        )

    def handle_goals_list(self, msg: Message, tg_user: TgUser) -> NoReturn:
        """Return goals list to user"""
        resp_goals: list[str] = [
            f'#{goal.id} {goal.title}'
            for goal in Goal.objects.filter(user_id=tg_user.user_id, is_deleted=False).order_by('created')
        ]
        if resp_goals:
            self.tg_client.send_message(msg.chat.id, '\n'.join(resp_goals))
        else:
            self.tg_client.send_message(msg.chat.id, '[goals are not found]')

    def handle_goal_categories_list(self, msg: Message, tg_user: TgUser) -> NoReturn:
        """Return categories list to user"""
        resp_categories: list[str] = [
            f'#{cat.id} {cat.title}'
            for cat in GoalCategory.objects.filter(
                board__participants__user_id=tg_user.user_id,
                is_deleted=False
            ).order_by('title')
        ]
        if resp_categories:
            self.tg_client.send_message(msg.chat.id, 'Select category\n' + '\n'.join(resp_categories))
        else:
            self.tg_client.send_message(msg.chat.id, '[categories are not found]')

    def handle_save_selected_category(self, msg: Message, tg_user: TgUser) -> NoReturn:
        """Return category to user"""
        if msg.text.isdigit():
            cat_id = int(msg.text)
            if GoalCategory.object.filter(
                    board__participants__user_id=tg_user.user_id,
                    board__participants__role_in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                    is_deleted=False,
                    id=cat_id
            ).exists():
                self.storage.update_data(chat_id=msg.chat.id, cat_id=cat_id)
                self.tg_client.send_message(msg.chat.id, '[set title]')
                self.storage.set_state(msg.chat.id, state=StateEnum.CHOSEN_CATEGORY)
            else:
                self.tg_client.send_message(msg.chat.id, '[Category not found or read only]')
        else:
            self.tg_client.send_message(msg.chat.id, '[Invalid category id]')

    def handle_save_new_cat(self, msg: Message, tg_user: TgUser) -> NoReturn:
        """New goal creation"""
        goal = NewGoal(**self.storage.get_data(tg_user.chat_id))
        goal.goal_title = msg.text
        if goal.is_completed:
            Goal.object.create(
                title=goal.goal_title,
                category_id=goal.cat_id,
                user_id=tg_user.user_id,
                due_date=datetime.now() + timedelta(days=7)
            )
            if GoalCategory.object.filter(
                    board__participants__role_in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                    is_deleted=False,
            ).exists():
                self.tg_client.send_message(msg.chat.id, '[New goal created]')
            else:
                self.tg_client.send_message(msg.chat.id, '[Access to create goal only for owner or writers]')
        else:
            self.tg_client.send_message(msg.chat.id, '[Something wrong]')

        self.storage.reset(tg_user.chat_id)

    def handle_verified_user(self, msg: Message, tg_user: TgUser) -> NoReturn:
        """Standard bot commands sent by user"""
        if msg.text == '/goals':
            self.handle_goals_list(msg, tg_user)

        elif msg.text == '/create':
            self.handle_goal_categories_list(msg, tg_user)
            self.storage.set_state(msg.chat.id, state=StateEnum.CREATE_CATEGORY_SELECT)
            self.storage.set_data(msg.chat.id, data=NewGoal().dict())

        elif msg.text == '/cancel' and self.storage.get_state(tg_user.chat_id):
            self.storage.reset(tg_user.chat_id)
            self.tg_client.send_message(msg.chat.id, '[canceled]')

        elif state := self.storage.get_state(tg_user.chat_id):
            match state:
                case StateEnum.CREATE_CATEGORY_SELECT:
                    self.handle_save_selected_category(msg, tg_user)
                case StateEnum.CHOSEN_CATEGORY:
                    self.handle_save_new_cat(msg, tg_user)
                case _:
                    logger.warning("Invalid State: %s", state)

        elif msg.text.startswith('/'):
            self.tg_client.send_message(msg.chat.id, '[unknown command]')

    def handle_message(self, msg: Message) -> NoReturn:
        """New message creation"""
        tg_user, _ = TgUser.objects.select_related('user').get_or_create(
            chat_id=msg.chat.id,
            defaults={
                'username': msg.from_.username
            }
        )

        if tg_user.user:
            self.handle_verified_user(msg=msg, tg_user=tg_user)
        else:
            self.handle_unverified_user(msg=msg, tg_user=tg_user)

    def handle(self, *args, **options) -> NoReturn:
        """Receiving bot notifications and sending response to user"""
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(msg=item.message)
                self.tg_client.send_message(chat_id=item.message.chat.id, text=item.message.text)
