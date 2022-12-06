from datetime import datetime

from dateutil.tz import UTC
from django.utils import timezone
import factory.fuzzy

from core.models import User
from goals.models import Board, GoalCategory, Goal, BoardParticipant


class BoardFactory(factory.django.DjangoModelFactory):
    """Test class for Board"""
    title = factory.fuzzy.FuzzyText(length=25, prefix='test', suffix='board')
    is_deleted = False
    created = timezone.now()
    updated = timezone.now()

    class Meta:
        model = Board


class UserFactory(factory.django.DjangoModelFactory):
    """Test for User"""
    first_name = "Andrey"
    last_name = "Markaryan"
    username = factory.Sequence(lambda n: 'user%d' % n)

    class Meta:
        model = User


class GoalCategoryFactory(factory.django.DjangoModelFactory):
    """Test for GoalCategory"""
    title = factory.fuzzy.FuzzyText(length=25, prefix='test', suffix='goalcategory')
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    is_deleted = False
    created = timezone.now()
    updated = timezone.now()

    class Meta:
        model = GoalCategory


class GoalFactory(factory.django.DjangoModelFactory):
    """Test for Goal"""
    title = factory.fuzzy.FuzzyText(length=25, prefix='test', suffix='goal')
    description = 'goal factory test'
    category = factory.SubFactory(GoalCategoryFactory)
    status = factory.fuzzy.FuzzyChoice([Goal.Status.to_do, Goal.Status.in_progress, Goal.Status.done])
    priority = factory.fuzzy.FuzzyChoice(
        [Goal.Priority.critical, Goal.Priority.low, Goal.Priority.medium, Goal.Priority.high])
    due_date = factory.fuzzy.FuzzyDateTime(datetime(2022, 11, 20, tzinfo=UTC), datetime(2022, 11, 21, tzinfo=UTC))
    user = factory.SubFactory(UserFactory)
    created = factory.fuzzy.FuzzyDateTime(datetime(2020, 11, 20, tzinfo=UTC), datetime(2021, 11, 20, tzinfo=UTC))
    updated = factory.fuzzy.FuzzyDateTime(datetime(2020, 11, 25, tzinfo=UTC), datetime(2021, 11, 25, tzinfo=UTC))

    class Meta:
        model = Goal


class BoardParticipantFactory(factory.django.DjangoModelFactory):
    """Test class for BoardParticipant"""
    class Meta:
        model = BoardParticipant

    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)
    role = BoardParticipant.Role.owner
