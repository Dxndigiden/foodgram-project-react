from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_COLOR,
    MIN_TIME_MESSAGE,
    MAX_TIME_MESSAGE,
    MIN_INGR_MESSAGE,
    MAX_INGR_MESSAGE,
    MIN_AMOUNT,
    MAX_AMOUNT_TIME,
    MAX_AMOUNT_INGR
)
from users.models import User


class Ingredient(models.Model):
    """Модель ингридиента"""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_NAME
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME,
        unique=True
    )
    color = ColorField(
        'Цвет',
        max_length=MAX_LENGTH_COLOR,
        unique=True
    )
    slug = models.SlugField(
        'Ссылка',
        max_length=MAX_LENGTH_NAME,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор рецепта',
    )
    text = models.TextField('Описание')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN_AMOUNT, message=MIN_TIME_MESSAGE),
            MaxValueValidator(MAX_AMOUNT_TIME, message=MAX_TIME_MESSAGE)
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингредиента в рецепте"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT, message=MIN_INGR_MESSAGE),
            MaxValueValidator(MAX_AMOUNT_INGR, message=MAX_INGR_MESSAGE)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount} '
        )


class Favorite(models.Model):
    """Модель избранного"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    """Модель Корзины"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в корзину'
