from django.contrib import admin

from core.constants import MIN_AMOUNT
from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    Favorite,
    ShoppingCart
)


class IngredientRecipeLine(admin.TabularInline):
    model = IngredientInRecipe
    min_num = MIN_AMOUNT
    validate_min = True

    extra = MIN_AMOUNT


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (IngredientRecipeLine,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    search_fields = ('author', 'name', 'tags')
    inlines = (IngredientRecipeLine,)

    def is_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
