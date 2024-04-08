from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_PSWRD
    )


class User(AbstractUser):
    """Модель пользователя"""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )
    username = models.CharField(
        'Уникальное имя пользователя',
        max_length=MAX_LENGTH_NAME,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_NAME
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_NAME
    )
    password = models.CharField(
        'Пароль',
        max_length=MAX_LENGTH_PSWRD,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='user',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='not_self_subscribe'
            ),
        ]
        ordering = ['following']

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
