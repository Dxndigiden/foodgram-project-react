import re

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from core.constants import (NOT_AMOUNT_MESSAGE,
                            MIN_AMOUNT_MESSAGE,
                            MIN_TAG_MESSAGE,
                            UNIQUE_TAG_MESSAGE,
                            VALIDATE_NAME_MESSAGE,
                            MIN_AMOUNT_TIME_OR_INGR,
                            MIN_TIME_MESSAGE,
                            MAX_TIME_MESSAGE,
                            MAX_AMOUNT_TIME,
                            MAX_INGR_MESSAGE,
                            MAX_AMOUNT_INGR,
                            ERR_ALREADY_RECIPE)
from recipes.models import (Ingredient,
                            Recipe,
                            Tag,
                            IngredientInRecipe,
                            Favorite,
                            ShoppingCart)
from users.models import User
from users.serializers import FoodUserSerializer


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиента"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(ModelSerializer):
    """Сериализатор тега"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор чтения рецепта"""

    tags = TagSerializer(many=True, read_only=True)
    author = FoodUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = SerializerMethodField('get_image_url')
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return (user and not user.is_anonymous
                and user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return (user and not user.is_anonymous
                and user.shopping_cart.filter(recipe=obj).exists())


class IngredientInRecipeWriteSerializer(ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт"""

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if not value:
            raise ValidationError(NOT_AMOUNT_MESSAGE)
        if value < MIN_AMOUNT_TIME_OR_INGR:
            raise ValidationError(MIN_AMOUNT_MESSAGE)
        if value >= MAX_AMOUNT_INGR:
            raise ValidationError(MAX_INGR_MESSAGE)
        return value


class RecipeWriteSerializer(ModelSerializer):
    """Сериализатор создания рецепта"""

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = FoodUserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        if value <= MIN_AMOUNT_TIME_OR_INGR:
            raise ValidationError(MIN_TIME_MESSAGE)
        if value >= MAX_AMOUNT_TIME:
            raise ValidationError(MAX_TIME_MESSAGE)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError(MIN_TAG_MESSAGE)
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError(UNIQUE_TAG_MESSAGE)
            tags_list.append(tag)
        return value

    def validate_name(self, value):
        if re.match(r'^[0-9\W]+$', value):
            raise ValidationError(VALIDATE_NAME_MESSAGE)
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients', [])
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data


class FavoriteAddSerializer(ModelSerializer):
    """Сериализатор добавления в избранное"""
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate_faworite(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(ERR_ALREADY_RECIPE)
        return data

    def create(self, validated_data):
        recipe = validated_data['recipe']
        user = validated_data['user']
        return Favorite.objects.create(user=user, recipe=recipe)

    def delete(self, data):
        user = data['user']
        recipe = data['recipe']
        return get_object_or_404(Favorite, user=user,
                                 recipe=recipe).delete()


class ShoppingCartAddSerializer(ModelSerializer):
    """Сериализатор добавления в избранное"""
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate_shoppingcart(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(ERR_ALREADY_RECIPE)
        return data

    def create(self, validated_data):
        recipe = validated_data['recipe']
        user = validated_data['user']
        return ShoppingCart.objects.create(user=user, recipe=recipe)

    def delete(self, data):
        user = data['user']
        recipe = data['recipe']
        return get_object_or_404(ShoppingCart, user=user,
                                 recipe=recipe).delete()
