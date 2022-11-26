from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from goals.models import BoardParticipant, Goal, GoalCategory, Board, GoalComment


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class BoardPermission(IsAuthenticated):
    """Permission for read or write access to Board"""
    def has_object_permission(self, request, view, obj: Board) -> bool:
        filters: dict = {"user": request.user, "board": obj}
        if request.method not in permissions.SAFE_METHODS:
            filters["role"] = BoardParticipant.Role.owner
        return BoardParticipant.objects.filter(**filters).exists()


class GoalCategoryPermission(IsAuthenticated):
    """Permission for read or write access to GoalCategory"""
    def has_object_permission(self, request, view, obj: GoalCategory) -> bool:
        filters: dict = {"user": request.user, "board": obj.board}
        if request.method not in permissions.SAFE_METHODS:
            filters["role__in"] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalPermission(IsAuthenticated):
    """Permission for read or write access to Goal"""
    def has_object_permission(self, request, view, obj: Goal) -> bool:
        filters: dict = {"user": request.user, "board": obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            filters["role__in"] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class CommentsPermission(IsAuthenticated):
    """Permission for read or write access to GoalComment"""
    def has_object_permission(self, request, view, obj: GoalComment) -> bool:
        return any((
            request.method in permissions.SAFE_METHODS,
            obj.user_id == request.user.id,
        ))
