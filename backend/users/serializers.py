from djoser.serializers import (UserCreateSerializer,
                                UserSerializer,
                                ValidationError)
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import User, Subscription
from api.serializers import RecipeShortSerializer
from core.constants import ERR_SUB_YOUSELF, ERR_ALREADY_SUB


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
    """Сериализатор просмотра подписки"""

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


class SubscribeAddSerializer(ModelSerializer):
    """Сериализатор создания подписки"""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def subscribe(self, data):
        user = data['user']
        author = data['author']
        Subscription.objects.create(user=user, author=author)
        return {'success': True}

    def validate_sub(self, obj):
        user = obj.get('user')
        author = obj.get('author')
        if user.following.filter(author=author).exists():
            raise ValidationError(ERR_ALREADY_SUB)
        if user == author:
            raise ValidationError(ERR_SUB_YOUSELF)
        return obj
