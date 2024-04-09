import re

from django.core.exceptions import ValidationError
from djoser.serializers import (UserCreateSerializer,
                                UserSerializer)
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import User, Subscription
from core.constants import (ERR_SUB_YOUSELF,
                            ERR_ALREADY_SUB,
                            VALIDATE_NAME_MESSAGE)
from recipes.recipeshort_serializers import RecipeShortSerializer


class FoodUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate_username(self, value):
        if not re.match(r'^[0-9\W]+$', value):
            raise ValidationError(VALIDATE_NAME_MESSAGE)
        return value


class FoodUserSerializer(UserSerializer):
    """Сериализатор пользователя"""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        user = [self.context.get('request').user
                if self.context.get('request')
                else None]
        return (user and not user.is_anonymous
                and obj.following.filter(
                    user=user).exists())


class SubscribeSerializer(FoodUserSerializer):
    """Сериализатор просмотра подписки"""

    recipes = SerializerMethodField(source='recipes.count',
                                    read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

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

    def create(self, data):
        user = data['user']
        author = data['author']
        Subscription.objects.create(user=user, author=author)
        return True

    def validate_sub(self, obj):
        user = obj.get('user')
        author = obj.get('author')
        if user.following.filter(author=author).exists():
            raise ValidationError(ERR_ALREADY_SUB)
        if user == author:
            raise ValidationError(ERR_SUB_YOUSELF)
        return obj
