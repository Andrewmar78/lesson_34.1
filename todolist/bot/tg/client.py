import requests

from bot.tg.models import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __int__(self, token: str):
        self.token = token

    def get_url(self, method: str) -> str:
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url('getUpdates')

        response = requests.get(url=url, params={"offset": offset, "timeout": timeout})

        return GetUpdatesResponse(**response.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url('sendMessage')

        # json = {"chat_id": chat_id, "text": text}
        # headers = {
        #     "accept": "application/json",
        #     "User-Agent": "Django application",
        #     "content-type": "application/json"
        # }
        # response = requests.post(url=url, headers=headers, json=json)
        response = requests.post(url=url, json={"chat_id": chat_id, "text": text})

        # return SendMessageResponse.Schema().load(response.json())
        return SendMessageResponse(**response.json())
