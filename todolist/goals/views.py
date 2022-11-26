from typing import Optional

from django.db import transaction
from django.db.models import Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters, generics
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter, BoardGoalCategoryFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import IsOwnerOrReadOnly, BoardPermission, GoalCategoryPermission, GoalPermission, \
    CommentsPermission
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, \
    BoardListSerializer, BoardSerializer


class BoardCreateView(generics.CreateAPIView):
    """New Board creation"""
    permission_classes = [BoardPermission]
    serializer_class = BoardCreateSerializer


class BoardListView(generics.ListAPIView):
    """Board list for board participant user"""
    model = Board
    permission_classes = [BoardPermission]
    serializer_class = BoardListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering = ['title', 'created']
    search_fields = ['title']

    def get_queryset(self) -> Optional[QuerySet[Board]]:
        return Board.objects.filter(participants__user_id=self.request.user.id, is_deleted=False)


class BoardView(generics.RetrieveUpdateDestroyAPIView):
    """Board Retrieve/Update/Destroy APIView"""
    model = Board
    permission_classes = [BoardPermission]
    serializer_class = BoardSerializer

    def get_queryset(self) -> Optional[QuerySet[Board]]:
        """List of Boards for board participant user"""
        return Board.objects.prefetch_related("participants").filter(
            participants__user_id=self.request.user.id,
            is_deleted=False)

    def perform_destroy(self, instance: Board) -> Board:
        """Update 'is_deleted' Board field and its Categories to True, also update the Goals status field
        to 'archived' field"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class GoalCategoryCreateView(CreateAPIView):
    """New GoalCategory creation"""
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """Board list for GoalCategory board participant user"""
    model = GoalCategory
    permission_classes = [GoalCategoryPermission]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = BoardGoalCategoryFilter
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self) -> Optional[QuerySet[GoalCategory]]:
        """List of all non-archived GoalCategories for board participant user"""
        if self.request.query_params.get('board'):
            return GoalCategory.objects.filter(board=self.request.query_params.get('board'), is_deleted=False)
        else:
            return GoalCategory.objects.prefetch_related('board__participants').filter(
                board__participants__user__id=self.request.user.id,
                is_deleted=False
            )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """GoalCategory Retrieve/Update/Destroy APIView"""
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermission, IsOwnerOrReadOnly]

    def get_queryset(self) -> Optional[QuerySet[GoalCategory]]:
        """List of GoalCategories for board participant user"""
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            board__participants__user__id=self.request.user.id,
            is_deleted=False
        )

    def perform_destroy(self, instance: GoalCategory) -> GoalCategory:
        """Update 'is_deleted' GoalCategory field to True, also update the Goals status field to 'archived' field"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
        return instance


class GoalCreateView(CreateAPIView):
    """Create a new Goal"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """Goal list for board participant user"""
    model = Goal
    permission_classes = [GoalPermission]
    serializer_class = GoalSerializer
    filterset_class = GoalDateFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
        ]
    ordering_fields = ["title", "-priority"]
    ordering = ["title", "-priority"]
    search_fields = ["title", "description"]

    def get_queryset(self) -> Optional[QuerySet[Goal]]:
        """Queryset of all Goals without archived status for board participant user"""
        return Goal.objects.select_related('user', 'category__board').filter(
            Q(category__board__participants__user_id=self.request.user.id) & ~Q(status=Goal.Status.archived)
        )


class GoalView(RetrieveUpdateDestroyAPIView):
    """Goal Retrieve/Update/Destroy APIView"""
    model = Goal
    permission_classes = [GoalPermission, IsOwnerOrReadOnly]
    serializer_class = GoalSerializer

    def get_queryset(self) -> Optional[QuerySet[Goal]]:
        """List of Goals without archived status for board participant user"""
        return Goal.objects.select_related('user', 'category__board').filter(
            Q(category__board__participants__user_id=self.request.user.id) & ~Q(status=Goal.Status.archived)
        )

    def perform_destroy(self, instance: Goal):
        """Update 'is_deleted' GoalCategory field to 'archived' status"""
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))
        return instance


class GoalCommentCreateView(CreateAPIView):
    """Create a new GoalComment"""
    permission_classes = [CommentsPermission]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    """GoalComments list for board participant user"""
    model = GoalComment
    permission_classes = [CommentsPermission]
    serializer_class = GoalCommentSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["goal"]
    ordering_fields = ["-created", "updated"]
    ordering = ["-created"]

    def get_queryset(self) -> Optional[QuerySet[GoalComment]]:
        """List of GoalComments to the Goal for board participant user"""
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            goal__category__board__participants__user_id=self.request.user.id,
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """GoalComment Retrieve/Update/Destroy APIView"""
    model = GoalComment
    permission_classes = [CommentsPermission, IsOwnerOrReadOnly]
    serializer_class = GoalCommentSerializer

    def get_queryset(self) -> Optional[QuerySet[GoalComment]]:
        """List of GoalComments to the Goal for board participant user"""
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            goal__category__board__participants__user_id=self.request.user.id,
        )
