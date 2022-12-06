import pytest
from django.urls import reverse
from django.utils import timezone
from goals.models import Board


@pytest.mark.django_db
class TestBoardCreateView:
    """Board creation test for authorised user"""
    def test_create_board_authorised(self, client, user):
        client.force_login(user=user)

        data = {"title": "New Board", }
        response = client.post(
            data=data,
            path=reverse('board-create'),
        )
        board = Board.objects.last()

        assert response.status_code == 201
        assert response.data == {
            "id": board.id,
            "created": timezone.localtime(board.created).isoformat(),
            "updated": timezone.localtime(board.updated).isoformat(),
            "title": "New Board",
            "is_deleted": False,
        }
