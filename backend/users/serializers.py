from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (Serializer,
                                        PrimaryKeyRelatedField,
                                        ValidationError)

from .models import User, Subscription
from api.serializers import RecipeShortSerializer
from core.constants import ERR_SUB_ALL, ERR_SUB_YOUSELF


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


class SubscribeAddSerializer(Serializer):
    """Сериализатор создания подписки"""

    user = PrimaryKeyRelatedField(read_only=True)
    author = PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if self.context['request'].method == 'POST':
            if user == author:
                raise ValidationError(ERR_SUB_YOUSELF)
        elif self.context['request'].method == 'DELETE':
            try:
                Subscription.objects.get(user=user, author=author)
            except Subscription.DoesNotExist:
                raise ValidationError(ERR_SUB_ALL)
        return data

    def create(self, data):
        return Subscription.objects.create(data)
