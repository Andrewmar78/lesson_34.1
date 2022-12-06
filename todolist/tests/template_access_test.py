from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_urls_uses_correct_template(self) -> None:
        """Checking of using template by URL-address"""
        templates_url_names: dict = {
            '/board/list/': 'board/list.html',
            '/goal_category/list/': 'goal_category/list.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                error_name: str = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)
