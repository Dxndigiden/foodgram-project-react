from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe


class RecipeShortSerializer(ModelSerializer):
    """Сериализатор краткого представления"""

    image = Base64ImageField(
        required=True,
        allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
