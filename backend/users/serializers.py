from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField

from .models import User
from api.serializers import RecipeShortSerializer


class FoodUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class FoodUserSerializer(UserSerializer):
    """Сериализатор пользователя"""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and obj.following.filter(
                    user=user).exists())


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
        try:
            return RecipeShortSerializer(obj.recipes.all()[:int(limit)],
                                         many=True).data if limit else None
        except ValueError:
            return None

    def get_recipes_count(self, obj):
        return obj.recipes.count()
