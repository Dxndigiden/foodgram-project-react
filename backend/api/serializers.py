"""
Данный сериализатор вынес отдельно в APi
тк юзается в обоих приложениях, и при переносе в сериализатор
приложения recipes получается зацикленный импорт
"most likely due to a circular import"
поэтому решил отдельно в апи, в core както не захотелось.
"""
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe


class RecipeShortSerializer(ModelSerializer):
    """Сериализатор краткого представления"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
