import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ErrorDetail

from core.models import User
from goals.models import Goal, GoalCategory, BoardParticipant


@pytest.mark.django_db
class TestGoalCreate:
    """Goal creation test for authorised user"""
    def test_create_goal_authorised(self, client, user, goal_category):
        user = user.user
        client.force_login(user=user)

        data = {
            "title": "Go sleeping",
            "description": "Go sleeping",
            "category": goal_category.id,
        }

        response = client.post(
            path=reverse('goals:create_goal'),
            data=data,
            content_type='application/json',
        )

        goal = Goal.objects.last()

        assert response.status_code == 201
        assert response.data == {
            "id": goal.id,
            "status": 1,
            "title": "Go sleeping",
            "description": "Go sleeping",
            "due_date": None,
            "category": goal_category.id,
            "priority": 1,
            "created": timezone.localtime(goal.created).isoformat(),
            "updated": timezone.localtime(goal.updated).isoformat(),
        }
