from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from users.models import User, Subscription

from api.pagination import FoodPagination
from core.constants import ERR_SUB_ALL
from .permissions import IsAdminOrCurrentUserOrReadOnly
from .serializers import (FoodUserSerializer,
                          SubscribeSerializer,
                          FoodUserCreateSerializer)


class FoodUserViewSet(UserViewSet):
    """Вьюсет пользователя"""

    queryset = User.objects.all()
    permission_classes = [IsAdminOrCurrentUserOrReadOnly]
    pagination_class = FoodPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return FoodUserSerializer
        return FoodUserCreateSerializer

    @action(
        methods=['post'], detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],)
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user
        following = get_object_or_404(User, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'following': following},)
            serializer.is_valid(raise_exception=True)
            serializer.save(following=following, user=user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        follow = user.user.filter(following=following)
        if not follow:
            return Response(
                {'errors': ERR_SUB_ALL},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated], url_path='me',)
    def get_me(self, request):
        serializer = FoodUserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
