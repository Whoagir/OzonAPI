from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Product
from .serializers import ProductSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    @method_decorator(cache_page(60 * 15))  # кэш на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)