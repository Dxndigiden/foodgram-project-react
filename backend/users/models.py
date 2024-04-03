from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from core.constants import MAX_LENGTH_NAME, MAX_LENGTH_EMAIL, ERR_SUB_YOUSELF


class User(AbstractUser):
    """Модель пользователя"""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
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
                fields=('user', 'author'),
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow'
            ),
        ]
        ordering = ('id',)

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.user == self.author:
            raise ValidationError(ERR_SUB_YOUSELF)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
