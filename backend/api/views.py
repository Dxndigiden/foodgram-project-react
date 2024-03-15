from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import User, Subscription

from core.constants import (ERR_SUB_YOUSELF,
                            ERR_ALREADY_SUB,
                            ERR_NOT_FOUND,
                            ERR_ALREADY_RECIPE,
                            ERR_DEL_RECIPE)
from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (FoodUserSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeShortSerializer,
                          RecipeWriteSerializer, SubscribeSerializer,
                          TagSerializer)


class FoodUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = FoodUserSerializer
    pagination_class = FoodPagination

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'new_password': ['This field is required.']},
                            status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following_user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)

        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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

        except IntegrityError:
            data = {'errors': ERR_ALREADY_SUB}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if user.is_authenticated:
            serializer = FoodUserSerializer(
                user,
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response({'detail': ERR_NOT_FOUND},
                            status=HTTP_401_UNAUTHORIZED)

    @me.mapping.post
    def me_post(self, request):
        return self.me(request)


class IngredientViewSet(ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = FoodPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        else:
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        else:
            return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': ERR_ALREADY_RECIPE},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': ERR_DEL_RECIPE},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient_name',
            'ingredient_measurement_unit'
        ).annotate(amount=models.Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'{user.get_full_name()} необходимо купить:\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient_name"]} '
            f'({ingredient["ingredient_measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
