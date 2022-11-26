from typing import Type

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """GoalCategory creation serializer"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")

    def validate_board(self, value: Board) -> Board:
        """Validation of board"""
        if value.is_deleted:
            raise serializers.ValidationError("Not allowed: board is deleted")

        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError("Allowed only for owners or writers")

        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    """GoalCategory serializer"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "board")


class GoalCreateSerializer(serializers.ModelSerializer):
    """Goal creation serializer"""
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        """Validation of goal category"""
        if self.context["request"].user != value.user:
            raise PermissionDenied("Вам запрещено создавать цели для данной категории")

        # if self.instance.category.board_id != value.board_id:
        #     raise serializers.ValidationError("Transfer from one project to another is not allowed")

        if not BoardParticipant.objects.filter(
                board_id=value.board.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user=self.context["request"].user,
        ).exists():
            raise PermissionDenied("Вам запрещено создавать цели для данной категории")

        return value


class GoalSerializer(serializers.ModelSerializer):
    """Goal serializer"""
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    def validate_category(self, value: Type[GoalCategory]) -> GoalCategory:
        """Validation of goal category"""
        if self.context["request"].user != value.user:
            raise PermissionDenied("Вам запрещены изменения целей для данной категории")
        return value


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """GoalComment creation serializer"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCommentSerializer(serializers.ModelSerializer):
    """GoalComment serializer"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "goal")


class BoardCreateSerializer(serializers.ModelSerializer):
    """Board creation serializer"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "is_deleted", "created", "updated")
        fields = "__all__"

    def create(self, validated_data: dict) -> Board:
        """Board creation, add user to it as owner"""
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(
            user=user, board=board, role=BoardParticipant.Role.owner
        )
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Board participant serializer"""
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    """Board serializer"""
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")

    def update(self, instance, validated_data: dict) -> Board:
        """Update Board, add users to the board participants"""
        owner = validated_data.pop("user")
        new_participants = validated_data.pop("participants")
        new_by_id = {part["user"].id: part for part in new_participants}

        old_participants = instance.participants.exclude(user=owner)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()
                else:
                    if (
                            old_participant.role
                            != new_by_id[old_participant.user_id]["role"]
                    ):
                        old_participant.role = new_by_id[old_participant.user_id]["role"]
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    board=instance, user=new_part["user"], role=new_part["role"]
                )

            if title := validated_data.get("title)"):
                instance.title = title
                instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Board list serializer"""
    class Meta:
        model = Board
        fields = "__all__"
