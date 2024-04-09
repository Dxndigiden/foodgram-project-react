from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Subscription, User


admin.site.unregister(Group)
admin.site.unregister(User)


class UserChangeForm(UserCreationForm):

    class Meta:
        model = User
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админка для пользователя"""

    add_form = UserChangeForm
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'get_recipe_count',
                    'get_follower_count', 'password')
    list_filter = ('email', 'username')
    add_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )

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
                                     follower_count=Count('follower',
                                                          distinct=True))
        return queryset


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписки"""

    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
