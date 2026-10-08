from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 12

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response
