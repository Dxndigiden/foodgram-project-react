from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_401_UNAUTHORIZED)
from users.models import User, Subscription

from core.constants import (ERR_SUB_YOUSELF,
                            ERR_ALREADY_SUB,
                            ERR_NOT_FOUND,
                            ERR_SUB_ALL)
from api.pagination import FoodPagination
from .serializers import (FoodUserSerializer,
                          SubscribeSerializer)


class FoodUserViewSet(UserViewSet):
    """Вьюсет пользователя"""

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
        queryset = User.objects.filter(following__user=request.user)
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
