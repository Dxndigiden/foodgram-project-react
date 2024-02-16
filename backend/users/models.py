from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q

MAX_LENGTH_STRING = 150
MAX_LENGTH_EMAIL = 254


class User(AbstractUser):
    """Модель юзера"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )
    username = models.CharField(
        'Уникальный никнейм',
        max_length=MAX_LENGTH_STRING,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_STRING
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_STRING
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок"""
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
            CheckConstraint(
                check=~Q(user=F('author')),
                name='prevent_self_follow'
            ),
        ]
        ordering = ('id',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
