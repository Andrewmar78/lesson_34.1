from pytest_factoryboy import register
from tests.factories import BoardFactory, UserFactory, GoalCategoryFactory, GoalFactory

pytest_plugins = "tests.fixtures"
register(BoardFactory)
register(UserFactory)
register(GoalCategoryFactory)
register(GoalFactory)
