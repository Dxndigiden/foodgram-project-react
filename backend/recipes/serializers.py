import re

from django.db import transaction, models
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from core.constants import (NOT_AMOUNT_MESSAGE,
                            NOT_REPEAT_MESSAGE,
                            MIN_AMOUNT_MESSAGE,
                            MIN_TAG_MESSAGE,
                            UNIQUE_TAG_MESSAGE,
                            VALIDATE_NAME_MESSAGE,
                            MIN_AMOUNT_TIME_OR_INGR,
                            MIN_TIME_MESSAGE,
                            MAX_TIME_MESSAGE,
                            MAX_AMOUNT_TIME)
from recipes.models import Ingredient, Recipe, Tag, IngredientInRecipe
from users.serializers import FoodUserSerializer


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиента"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """Сериализатор тега"""

    class Meta:
        model = Tag
        fields = '__all__'


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

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=models.F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.shopping_cart.filter(recipe=obj).exists()


class IngredientInRecipeWriteSerializer(ModelSerializer):
    """Сериализатор ингредиента в рецепте"""

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(NOT_AMOUNT_MESSAGE)
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(NOT_REPEAT_MESSAGE)
            if item['amount'] <= 0:
                raise ValidationError(MIN_AMOUNT_MESSAGE)
            ingredients_list.append(ingredient)
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
        elif value >= MAX_AMOUNT_TIME:
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

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        self.validate_name(validated_data.get('name', ''))
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        self.validate_name(validated_data.get('name', ''))
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data
