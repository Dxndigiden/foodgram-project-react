from django.contrib import admin

from core.constants import MIN_AMOUNT
from .models import (Ingredient,
                     Tag,
                     Recipe,
                     IngredientInRecipe,
                     Favorite,
                     ShoppingCart)


class IngredientRecipeInLine(admin.TabularInline):
    """Инлайн ингредиента в рецепте"""

    model = IngredientInRecipe
    min_num = MIN_AMOUNT
    validate_min = True

    extra = MIN_AMOUNT


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиента"""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (IngredientRecipeInLine,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тега"""

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для тега"""

    list_display = ('id', 'name', 'author')
    search_fields = ('author', 'name', 'tags')
    inlines = (IngredientRecipeInLine,)

    def is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного"""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для корзины"""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
