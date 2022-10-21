# from django.contrib.auth.hashers import make_password
# from django.contrib.auth.password_validation import validate_password
#
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
#
# from core.models import User
#
#
# class PasswordField(serializers.CharField):
#     """Валидация пароля"""
#     def __init__(self, **kwargs):
#         kwargs["style"] = {"input": "password"}
#         kwargs.setdefault("write_only", True)
#         super().__init__(**kwargs)
#         self.validators.append(validate_password)
#
#
# class CreateUserSerializer(serializers.ModelSerializer):
#     password = PasswordField(required=True)
#     password_repeat = PasswordField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')
#
#     def validate(self, attrs: dict):
#         """Проверка соответствия пароля и повтора пароля"""
#         if attrs['password'] != attrs['password_repeat']:
#             raise ValidationError('Passwords are not the same')
#         return attrs
#
#     def create(self, validated_data: dict):
#         """Удаляем лишнее, чтобы не создавался User с password_repeat, и шифруем пароль"""
#         del validated_data['password_repeat']
#         validated_data['password'] = make_password(validated_data['password'])
#         return super(CreateUserSerializer, self).create(validated_data)
