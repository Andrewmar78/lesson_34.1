from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    pass

    # ADMIN = "admin"
    # USER = "user"
    # ROLES = ((ADMIN, "Администратор"), (USER, "Пользователь"))
    #
    # phone = models.CharField(max_length=20, null=True)
    # email = models.EmailField(unique=True, max_length=50)
    # role = models.CharField(max_length=5, null=True, choices=ROLES, default=USER)
    # image = models.ImageField(upload_to="user_images/", null=True)
    #
    # USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    #
    # class Meta:
    #     verbose_name = "Пользователь"
    #     verbose_name_plural = "Пользователи"
    #     ordering = ["email"]
    #
    # def __str__(self):
    #     return self.email
