from rest_framework import viewsets, generics, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, PriceHistory, Alert, UserProfile, Cart, CartItem, SyncLog, ProductGroup, ProductVariant
from .serializers import ProductSerializer, PriceHistorySerializer, AlertSerializer, UserProfileSerializer, CartSerializer, CartItemSerializer, ProductGroupSerializer, ProductGroupDetailSerializer, ProductVariantSerializer
from django.db.models import Min, Max, Avg, Case, When, Q, BooleanField, F, Sum
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint para visualizar e atualizar perfil do usuário
    GET /api/perfil/ - Obtém dados do perfil
    PUT /api/perfil/ - Atualiza dados do perfil
    PATCH /api/perfil/ - Atualiza parcialmente o perfil
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'✅ Perfil atualizado: {request.user.email}')
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f'❌ Erro ao atualizar perfil: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'✅ Perfil atualizado (PATCH): {request.user.email}')
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f'❌ Erro ao atualizar perfil: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_avatar(self, request):
        """
        Deletar avatar do usuário - LGPD Compliance (Direito ao Esquecimento)
        DELETE /api/perfil/delete_avatar/
        """
        profile = self.get_object()
        
        if profile.avatar:
            # Deletar arquivo fisicamente
            if profile.avatar.storage.exists(profile.avatar.name):
                profile.avatar.storage.delete(profile.avatar.name)
                logger.info(f'🗑️  Avatar deletado para: {request.user.email}')
        
        # Limpar campo de avatar
        profile.avatar = None
        profile.save()
        
        return Response(
            {'success': True, 'message': 'Avatar deletado com sucesso'},
            status=status.HTTP_200_OK
        )
    
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class CartViewSet(viewsets.ViewSet):
    """
    API endpoint para gerenciar o carrinho de compras do usuário.
    GET /api/carrinho/ - Obtém carrinho com todos os itens
    POST /api/carrinho/adicionar/ - Adiciona produto ao carrinho
    POST /api/carrinho/remover/ - Remove produto do carrinho
    PATCH /api/carrinho/limpar/ - Limpa o carrinho
    """
    permission_classes = [IsAuthenticated]
    
    def get_cart(self, request):
        """Helper para obter ou criar carrinho do usuário"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        if created:
            logger.info(f'✅ Novo carrinho criado para {request.user.email}')
        return cart
    
    def list(self, request):
        """Retorna o carrinho com todos os itens"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='adicionar')
    def adicionar(self, request):
        """Adiciona um produto ao carrinho"""
        cart = self.get_cart(request)
        product_id = request.data.get('product_ID')
        quantidade = int(request.data.get('quantidade', 1))
        
        if not product_id:
            return Response(
                {'error': 'product_ID é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(product_ID=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Produto {product_id} não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantidade': quantidade, 'preco_no_momento': product.price}
        )
        
        if not created:
            # Atualizar quantidade se o item já existe
            cart_item.quantidade += quantidade
            cart_item.save()
        
        # Atualizar total de itens do carrinho
        cart.total_itens = cart.itens.aggregate(total=Sum('quantidade'))['total'] or 0
        cart.save()
        
        logger.info(f'✅ Produto {product_id} adicionado ao carrinho de {request.user.email}')
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='remover')
    def remover(self, request):
        """Remove um produto do carrinho"""
        cart = self.get_cart(request)
        product_id = request.data.get('product_ID')
        
        if not product_id:
            return Response(
                {'error': 'product_ID é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            
            # Atualizar total de itens do carrinho
            cart.total_itens = cart.itens.aggregate(total=Sum('quantidade'))['total'] or 0
            cart.save()
            
            logger.info(f'✅ Produto {product_id} removido do carrinho de {request.user.email}')
        except CartItem.DoesNotExist:
            return Response(
                {'error': f'Produto {product_id} não encontrado no carrinho'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='limpar')
    def limpar(self, request):
        """Limpa todo o carrinho"""
        cart = self.get_cart(request)
        cart.itens.all().delete()
        cart.total_itens = 0
        cart.save()
        
        logger.info(f'✅ Carrinho de {request.user.email} foi limpo')
        serializer = CartSerializer(cart)
        return Response(serializer.data)


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
    def stats(self, request):
        """Retorna estatísticas do agregador"""
        from django.db.models import Count, Max
        from datetime import datetime
        
        total_products = Product.objects.count()
        total_stores = Product.objects.values('store').distinct().count()
        
        # Data da última sincronização (quando o scraper rodou)
        latest_sync = SyncLog.objects.filter(status='success').order_by('-timestamp').first()
        if latest_sync:
            last_update = latest_sync.timestamp
        else:
            last_update = timezone.now()
        
        return Response({
            'total_products': total_products,
            'total_stores': total_stores,
            'last_update': last_update
        })

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


class ProductGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint para grupos de produtos (deduplicados).
    GET /api/product-groups/ - Lista todos os grupos
    GET /api/product-groups/{id}/ - Detalhes do grupo com histórico de preços
    """
    queryset = ProductGroup.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['menu', 'type', 'created_at']
    search_fields = ['canonical_name']
    ordering_fields = ['lowest_price', 'average_price', 'created_at', 'variant_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductGroupDetailSerializer
        return ProductGroupSerializer
    
    @action(detail=True, methods=['get'])
    def price_chart_data(self, request, pk=None):
        """
        Retorna dados para gráfico de preços (até 360 pontos).
        GET /api/product-groups/{id}/price_chart_data/
        """
        group = self.get_object()
        history = group.price_history.all().order_by('-date')[:360]
        
        chart_data = {
            'dates': [],
            'prices': [],
            'lowest_prices': [],
            'highest_prices': [],
            'average_prices': []
        }
        
        for entry in reversed(history):
            chart_data['dates'].append(entry.date.strftime('%Y-%m-%d %H:%M'))
            chart_data['prices'].append(float(entry.price))
            chart_data['lowest_prices'].append(float(group.lowest_price))
            chart_data['highest_prices'].append(float(group.highest_price))
            chart_data['average_prices'].append(float(group.average_price))
        
        return Response({
            'group_id': group.id,
            'group_name': group.canonical_name,
            'chart_data': chart_data,
            'current_lowest': float(group.lowest_price),
            'current_highest': float(group.highest_price),
            'current_average': float(group.average_price),
            'variant_count': group.variant_count,
            'last_updated': group.last_updated.isoformat()
        })


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para variantes de produtos.
    GET /api/product-variants/ - Lista todas as variantes
    GET /api/product-variants/{id}/ - Detalhes da variante
    """
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['group', 'store_name', 'is_available']
    ordering_fields = ['price', 'last_price_check']
    ordering = ['price']
    
    @action(detail=False, methods=['get'])
    def by_group(self, request):
        """Retorna variantes de um grupo específico"""
        group_id = request.query_params.get('group_id')
        if not group_id:
            return Response({'error': 'group_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        variants = self.queryset.filter(group_id=group_id).order_by('price')
        serializer = self.get_serializer(variants, many=True)
        return Response(serializer.data)