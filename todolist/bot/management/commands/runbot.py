from django.core.management import BaseCommand
from backend.settings import TG_TOKEN
from bot.tg.client import TgClient


class Command(BaseCommand):
    def __int__(self, *args, **kwargs):
        self.tg_client = TgClient(TG_TOKEN)
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.tg_client.send_message(chat_id=item.message.chat.id, text=item.message.text)

