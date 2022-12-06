import pytest
from django.urls import reverse
from django.utils import timezone
from goals.models import GoalCategory


@pytest.mark.django_db
class TestGoalCategoryCreateView:
    """Goal category creation for authorised user"""
    def test_create_category_authorised(self, client, board_participant):
        user = board_participant.user
        board = board_participant.board
        client.force_login(user=user)

        data = {"title": "Sleeping", "board": board.id, }
        response = client.post(
            path=reverse('goals:create_category'),
            data=data,
            content_type='application/json',
        )
        category = GoalCategory.objects.last()

        assert response.status_code == 201
        assert response.data == {
            "id": category.id,
            "created": timezone.localtime(category.created).isoformat(),
            "updated": timezone.localtime(category.updated).isoformat(),
            "title": "Sleeping",
            "is_deleted": False,
            "board": board.id,
        }
