import pytest
from django.utils import timezone
from rest_framework.exceptions import ErrorDetail

from core.serializers import CreateUserSerializer
from goals.models import GoalCategory, Goal, BoardParticipant
from goals.serializers import GoalCategorySerializer
from tests.factories import UserFactory


@pytest.mark.django_db
class TestGoalCategoryView:
    def test_category_detail_by_unauthorised(self, client, user_category):
        response = client.get(path=f"/goals/models/{user_category.id}")
        assert response.status_code == 401

    def test_category_retrieve_by_authorised(self, client, board_participant, user_category):
        client.force_login(user=board_participant.user)
        expected_response = GoalCategorySerializer(user_category).data
        response = client.get(path=f"/goals/models/{user_category.id}")
        assert response.status_code == 200
        assert response.data == expected_response

    def test_category_update_by_authorised(self, client, board_participant, user_category):
        client.force_login(user=board_participant.user)
        data = {'title': 'Business'}

        response = client.patch(
            path=f"/goals/models/{user_category.id}",
            data=data,
            content_type='application/json',
        )
        category = GoalCategory.objects.latest('updated')

        assert response.status_code == 200
        assert response.data == {
            "id": category.id,
            "user": CreateUserSerializer(user_category.user).data,
            "created":  timezone.localtime(category.created).isoformat(),
            "updated": timezone.localtime(category.updated).isoformat(),
            "title": "Sleeping",
            "is_deleted": user_category.is_deleted,
            "board": user_category.board.id
        }

    def test_category_destroy_by_authorised(self, client, board_participant, user_category):
        client.force_login(user=board_participant.user)

        response = client.delete(path=f"/goals/models/{user_category.id}", )
        category = GoalCategory.objects.latest('updated')
        goal = Goal.objects.get(category=category)

        assert response.status_code == 204
        assert category.is_deleted is True
        assert goal.status == Goal.Status.archived

    def test_category_retrieve_by_nonallowed(self, client, user_category):
        non_allowed_user = UserFactory()
        client.force_login(user=non_allowed_user)
        response = client.get(path=f"/goals/models/{user_category.id}")
        assert response.status_code == 404

    def test_category_update_by_reader(self, client, board_participant, user_category):
        board_participant.role = BoardParticipant.Role.reader
        board_participant.save()
        client.force_login(user=board_participant.user)
        data = {'title': 'Sleeping'}
        response = client.patch(path=f"/goals/models/{user_category.id}", data=data, content_type='application/json', )

        assert response.status_code == 403
        assert response.data == {'detail': ErrorDetail(string='Доступно только чтение', code='permission_denied')}

    def test_category_destroy_by_writer(self, client, board_participant, user_category):
        board_participant.role = BoardParticipant.Role.writer
        board_participant.save()
        client.force_login(user=board_participant.user)
        response = client.delete(path=f"/goals/models/{user_category.id}", )
        category = GoalCategory.objects.latest('updated')
        goal = Goal.objects.get(category=category)

        assert response.status_code == 204
        assert category.is_deleted is True
        assert goal.status == Goal.Status.archived
