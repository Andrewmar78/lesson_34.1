from http import HTTPStatus
from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_static_page(self) -> None:
        """Page access by URL test"""
        pages: tuple = ('/board/list/', '/goal_category/list/', '/goal/list/', '/goal_comment/list/')
        for page in pages:
            response = self.guest_client.get(page)
            error_name: str = f'Ошибка: нет доступа к странице {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)
