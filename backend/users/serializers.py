from djoser.serializers import (UserCreateSerializer,
                                UserSerializer,)
from rest_framework.fields import SerializerMethodField
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ReadOnlyField
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import User, Subscription
from recipes.recipeshort_serializers import RecipeShortSerializer
from core.constants import ERR_SUB_YOUSELF, ERR_ALREADY_SUB


class FoodUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)
        extra_kwargs = {
            'password': {'write_only': True},
        }


class FoodUserSerializer(UserSerializer):
    """Сериализатор пользователя"""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous or (user == obj):
            return False
        return obj.following.filter(user=user).exists()


class SubscribeSerializer(FoodUserSerializer):
    """Сериализатор просмотра и создания подписки"""

    email = ReadOnlyField(source='following.email')
    id = ReadOnlyField(source='following.id')
    username = ReadOnlyField(source='following.username')
    first_name = ReadOnlyField(source='following.first_name')
    last_name = ReadOnlyField(source='following.last_name')
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', )

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        recipes = obj.following.recipe.all()
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
            return None
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.following.recipe.count()

    def validate(self, data):
        following = self.context.get('following')
        user = self.context['request'].user
        if user.user.filter(following=following).exists():
            raise ValidationError(
                message=ERR_ALREADY_SUB,
                status=HTTP_400_BAD_REQUEST
            )
        if user == following:
            raise ValidationError(
                message=ERR_SUB_YOUSELF,
                status=HTTP_400_BAD_REQUEST,
            )
        return data
