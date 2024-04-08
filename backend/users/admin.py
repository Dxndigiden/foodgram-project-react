from django.contrib import admin
from django.db.models import Count

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для пользователя"""

    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'get_recipe_count',
                    'get_follower_count', 'password')
    list_filter = ('email', 'username')

    def get_recipe_count(self, obj):
        return obj.recipes.count()

    def get_follower_count(self, obj):
        return obj.follower.count()

    get_recipe_count.short_description = 'Кол-во рецептов'
    get_follower_count.short_description = 'Кол-во подписчиков'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(recipe_count=Count('recipes',
                                                        distinct=True),
                                     follower_count=Count('user',
                                                          distinct=True))
        return queryset


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписки"""

    list_display = ('id', 'user', 'following')
    search_fields = ('user',)
    list_filter = ('user', )
