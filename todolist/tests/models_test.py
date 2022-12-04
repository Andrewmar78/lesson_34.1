from django.test import TestCase

from core.models import User
from goals.models import Board, GoalCategory, Goal


class BoardModelTest(TestCase):
    """Board model test"""
    board = Board.objects.get(id=1)

    @classmethod
    def setUpTestData(cls) -> None:
        Board.objects.create(title='Test_board')

    def test_title_label(self) -> None:
        # board = Board.objects.get(id=1)
        field_label = self.board._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_is_deleted_label(self) -> None:
        # board = Board.objects.get(id=1)
        field_label = self.board._meta.get_field('is_deleted').verbose_name
        self.assertEquals(field_label, 'Удалена')

    def test_title_max_length(self) -> None:
        # board = Board.objects.get(id=1)
        max_length = self.board._meta.get_field('title').max_length
        self.assertEquals(max_length, 255)

    def test_object_name_is_title_and_is_deleted(self) -> None:
        # board = Board.objects.get(id=1)
        expected_object_name = '%s, %s' % (self.board.title, self.board.is_deleted)
        self.assertEquals(expected_object_name, str(self.board))

    def test_get_absolute_url(self) -> None:
        # board = Board.objects.get(id=1)
        self.assertEquals(self.board.get_absolute_url(), '/board/1')


class GoalCategoryTest(TestCase):
    """Category model test"""
    @classmethod
    def setUpTestData(cls) -> None:
        GoalCategory.objects.create(title='Test_category')

    def test_title_label(self) -> None:
        category = GoalCategory.objects.get(id=1)
        field_label = category._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_is_deleted_label(self) -> None:
        category = GoalCategory.objects.get(id=1)
        field_label = category._meta.get_field('is_deleted').verbose_name
        self.assertEquals(field_label, 'Удалена')

    def test_title_max_length(self) -> None:
        category = GoalCategory.objects.get(id=1)
        max_length = category._meta.get_field('title').max_length
        self.assertEquals(max_length, 255)

    def test_object_name_is_title_and_is_deleted(self) -> None:
        category = GoalCategory.objects.get(id=1)
        expected_object_name = '%s, %s' % (category.title, category.is_deleted)
        self.assertEquals(expected_object_name, str(category))

    def test_get_absolute_url(self) -> None:
        category = GoalCategory.objects.get(id=1)
        self.assertEquals(category.get_absolute_url(), '/goal_category/1')


# class GoalCategoryForeignModelTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user_ = 'Test_user'
#         cls.user = User.objects.create(username=cls.user_)
#         cls.category = GoalCategory.objects.create(title='Category test', user=cls.user)
#
#     def test_if_category_has_required_user(self):
#         self.assertEqual(self.category.user.name, self.user_)


class GoalCategoryForeignModelTest(TestCase):
    def test_if_category_has_required_user(self):
        user = User(username='Test_user')
        user.save()
        category = GoalCategory(name="Test Category", user=user)
        category.save()

        record = GoalCategory.objects.get(id=1)
        self.assertEqual(record.user.username, 'Test_user')


class GoalModelTest(TestCase):
    """Goal model test"""
    goal = Goal.objects.get(id=1)

    @classmethod
    def setUpTestData(cls) -> None:
        Goal.objects.create(title='Test_goal', description="Test_description")

    def test_title_label(self) -> None:
        field_label = self.goal._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_description_label(self) -> None:
        field_label = self.goal._meta.get_field('description').verbose_name
        self.assertEquals(field_label, 'description')

    def test_due_date_label(self) -> None:
        field_label = self.goal._meta.get_field('due_date').verbose_name
        self.assertEquals(field_label, 'Дата выполнения')

    def test_title_max_length(self) -> None:
        max_length = self.goal._meta.get_field('title').max_length
        self.assertEquals(max_length, 255)

    def test_object_name_is_title_and_description(self) -> None:
        expected_object_name = '%s, %s' % (self.goal.title, self.goal.description)
        self.assertEquals(expected_object_name, str(self.goal))

    def test_get_absolute_url(self) -> None:
        self.assertEquals(self.goal.get_absolute_url(), '/goal/1')
