from typing import Any
import pytest

from goals.models import GoalCategory
from tests.factories import GoalCategoryFactory, GoalFactory


@pytest.fixture()
def board_participant(board_participant) -> Any:
    """Return board participant"""
    return board_participant


@pytest.fixture()
def user_board(board_participant) -> Any:
    """Return user board"""
    return board_participant.board


@pytest.fixture()
def user_category(board_participant):
    """Return user category and goal"""
    user_category = GoalCategoryFactory(board=board_participant.board, user=board_participant.user)
    goal = GoalFactory(category=user_category, user=board_participant.user)

    return list[user_category, goal]


@pytest.fixture()
def user_categories(board_participant):
    """Return user categories"""
    GoalCategoryFactory.create_batch(size=5, board=board_participant.board, user=board_participant.user)
    return GoalCategory.objects.all()
