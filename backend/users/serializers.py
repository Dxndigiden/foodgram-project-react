from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import User, Subscription
from recipes.models import Recipe


class FoodUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class FoodUserSerializer(UserSerializer):
    """Сериализатор пользователя"""

    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and Subscription.objects.filter(
                    user=user, author=obj).exists())

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', )


class RecipeShortSerializer(ModelSerializer):
    """Сериализатор краткого представления"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(FoodUserSerializer):
    """Сериализатор подписки"""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', )

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = (
            obj.recipes.all()[:int(limit)]
            if limit is not None else obj.recipes.all()
        )
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
