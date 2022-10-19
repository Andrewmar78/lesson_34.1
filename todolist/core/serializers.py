# from djoser.serializers import UserCreateSerializer
# from rest_framework import serializers
#
# from core.models import User
#
#
# class UserRegistrationSerializer(UserCreateSerializer):
#     """Создание пользователя переопределением сериалайзера, который использует djoser"""
#     class Meta:
#         model = User
#         fields = '__all__'
#
#     def create(self, validated_data):
#         """Хэширование пароля, сохранение пользователя в базе"""
#         user = super().create(validated_data)
#         user.set_password(user.password)
#         user.save()
#
#         return user
#
#
# class CurrentUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'
