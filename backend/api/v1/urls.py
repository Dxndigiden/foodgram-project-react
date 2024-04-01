from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import FoodUserViewSet

router_v1 = DefaultRouter()
router_v1.register(r'users', FoodUserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscribe/', FoodUserViewSet.as_view(
        {'get': 'subscriptions'}), name='subscriptions-list'),
    path('users/<int:pk>/subscribe/',
         FoodUserViewSet.as_view({'post': 'subscribe',
                                  'delete': 'subscribe'}),
         name='subscribe-unsubscribe'),
]
