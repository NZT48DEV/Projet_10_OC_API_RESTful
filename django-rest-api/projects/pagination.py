from rest_framework.pagination import PageNumberPagination


class ContributorProjectPagination(PageNumberPagination):
    """Pagination personnalisée : 1 projet par page"""

    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 10
