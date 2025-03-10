from rest_framework.pagination import PageNumberPagination


class FoodPagination(PageNumberPagination):
    """Пагинатор страниц"""

    page_size_query_param = 'limit'
