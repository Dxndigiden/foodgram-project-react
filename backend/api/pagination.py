from rest_framework.pagination import PageNumberPagination

from constants.constants import PG_SIZE


class LimitPageNumberPagination(PageNumberPagination):
    page_size = PG_SIZE
    page_size_query_param = 'limit'
