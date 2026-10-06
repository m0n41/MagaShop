from rest_framework.pagination import LimitOffsetPagination

class ProductAPIListPagination(LimitOffsetPagination):
    default_limit = 3
    limit_query_param = "limit"
    max_limit = 10