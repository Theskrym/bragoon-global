from rest_framework import viewsets, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, PriceHistory, Alert
from .serializers import ProductSerializer, PriceHistorySerializer, AlertSerializer
from django.db.models import Min, Max, Avg, Case, When, Q, BooleanField
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['menu', 'type', 'store', 'filter', 'subfilter']
    search_fields = ['name']
    lookup_field = 'product_ID'

    @action(detail=False)
    def filter_options(self, request):
        menus = Product.objects.values_list('menu', flat=True).distinct().exclude(menu__isnull=True).exclude(menu='')
        logger.info('Menus retrieved: %s', list(menus))

        type_dict = {}
        for menu in menus:
            types = Product.objects.filter(menu=menu).values_list('type', flat=True).distinct().exclude(type__isnull=True).exclude(type='')
            type_dict[menu] = list(types)
        logger.info('Type dictionary: %s', type_dict)

        filter_dict = {}
        for menu in menus:
            for type_ in type_dict.get(menu, []):
                key = f"{menu}_{type_}"
                filters = Product.objects.filter(menu=menu, type=type_).values_list('filter', flat=True).distinct()
                filter_dict[key] = [f for f in filters if f]
                logger.info('Filters for %s: %s', key, filter_dict[key])

        subfilter_dict = {}
        for menu in menus:
            for type_ in type_dict.get(menu, []):
                for filter_ in filter_dict.get(f"{menu}_{type_}", []):
                    key = f"{menu}_{type_}_{filter_}"
                    subfilters = Product.objects.filter(menu=menu, type=type_, filter=filter_).values_list('subfilter', flat=True).distinct()
                    subfilter_dict[key] = [sf for sf in subfilters if sf]
                    logger.info('Subfilters for %s: %s', key, subfilter_dict[key])

        stores = Product.objects.values_list('store', flat=True).distinct().exclude(store__isnull=True).exclude(store='')
        logger.info('Stores retrieved: %s', list(stores))

        response_data = {
            'stores': list(stores),
            'menus': list(menus),
            'type': type_dict,
            'filter': filter_dict,
            'subfilter': subfilter_dict
        }
        logger.info('Filter options response: %s', response_data)

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        params = request.query_params
        page = int(params.get('page', 1))
        page_size = int(params.get('page_size', 50))
        sort = params.get('sort', 'price_asc')
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Anotar produtos indisponíveis (preço = 0 ou nulo)
        queryset = queryset.annotate(
            is_unavailable=Case(
                When(Q(price=0) | Q(price__isnull=True), then=True),
                default=False,
                output_field=BooleanField()
            )
        )
        
        # Aplicar ordenação: indisponíveis sempre por último, depois ordenar por critério selecionado
        if sort == 'price_asc':
            queryset = queryset.order_by('is_unavailable', 'price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('is_unavailable', '-price')
        elif sort == 'rating_desc':
            queryset = queryset.order_by('is_unavailable', '-rating')
        else:
            queryset = queryset.order_by('is_unavailable')
        
        total_items = queryset.count()
        total_pages = (total_items + page_size - 1) // page_size
        
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = self.get_serializer(queryset[start:end], many=True)
        
        return Response({
            'products': serializer.data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_items': total_items,
                'page_size': page_size
            }
        })

class PriceHistoryView(generics.ListAPIView):
    serializer_class = PriceHistorySerializer
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        six_months_ago = timezone.now() - timedelta(days=180)
        return PriceHistory.objects.filter(
            product__product_ID=product_id,
            date__gte=six_months_ago
        ).order_by('date')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        product = Product.objects.get(product_ID=self.kwargs['product_id'])
        similar_products = Product.objects.filter(
            name__icontains=product.name.split()[0]
        ).exclude(product_ID=product.product_ID)
        
        stats = {
            'current': float(product.price),
            'average': float(queryset.aggregate(avg=Avg('price'))['avg'] or 0),
            'minimum': float(queryset.aggregate(min=Min('price'))['min'] or 0),
            'maximum': float(queryset.aggregate(max=Max('price'))['max'] or 0),
            'lowest_6_months': float(queryset.order_by('price').first().price if queryset.exists() else 0)
        }
        
        return Response({
            'price_history': serializer.data,
            'stats': stats,
            'similar_products': ProductSerializer(similar_products, many=True).data
        })

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    queryset = Alert.objects.all()
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=True, methods=['post'])
    def check_price(self, request, pk=None):
        alert = self.get_object()
        product = alert.product
        price_history = PriceHistory.objects.filter(product=product).order_by('-date')[:1]
        
        if price_history.exists():
            current_price = price_history[0].price
            if current_price <= alert.target_price:
                return Response({
                    'status': 'triggered',
                    'message': f'O preço do produto {product.name} atingiu R${current_price}'
                })
        
        return Response({
            'status': 'not_triggered',
            'message': 'O alerta não foi acionado'
        })