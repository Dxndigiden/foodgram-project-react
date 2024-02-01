from django.contrib import admin
from django.db.models import Count

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'get_recipe_count',
                    'get_follower_count', 'password')
    list_filter = ('email', 'username')

    def get_recipe_count(self, obj):
        return obj.recipes.count()

    def get_follower_count(self, obj):
        return obj.follower.count()

    get_recipe_count.short_description = 'Количество рецептов'
    get_follower_count.short_description = 'Количество подписчиков'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(recipe_count=Count('recipes',
                                                        distinct=True),
                                     follower_count=Count('follower',
                                                          distinct=True))
        return queryset


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
