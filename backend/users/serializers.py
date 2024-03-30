from django.db import IntegrityError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.pagination import FoodPagination
from core.constants import (ERR_SUB_YOUSELF,
                            ERR_ALREADY_SUB,
                            ERR_SUB_ALL)
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

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and Subscription.objects.filter(
                    user=user, author=obj).exists())


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
    queryset = User.objects.all()
    serializer_class = FoodUserSerializer
    pagination_class = FoodPagination

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', )

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)

        try:
            if request.method == 'POST':
                if user == author:
                    data = {'errors': ERR_SUB_YOUSELF}
                    return Response(data=data,
                                    status=status.HTTP_400_BAD_REQUEST)

                Subscription.objects.create(user=user, author=author)
                serializer = SubscribeSerializer(author,
                                                 context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

            elif request.method == 'DELETE':
                subscribe = Subscription.objects.filter(user=user,
                                                        author=author)
                if subscribe.exists():
                    subscribe.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    data = {'errors': ERR_SUB_ALL}
                    return Response(data=data,
                                    status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            data = {'errors': ERR_ALREADY_SUB}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = (
            obj.recipes.all()[:int(limit)]
            if limit is not None else obj.recipes.all()
        )
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
