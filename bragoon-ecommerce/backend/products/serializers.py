from rest_framework import serializers
from .models import Product, PriceHistory, Alert, UserProfile, Cart, CartItem, ProductGroup, ProductVariant

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'product_ID',
            'name',
            'price',
            'rating',
            'review_count',
            'store',
            'image_url',
            'product_link',
            'affiliate_link',
            'menu',
            'type',
            'filter',
            'subfilter'
        ]

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['date', 'price']

class AlertSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'product', 'target_price', 'created_at', 'is_active', 'notification_type']
        read_only_fields = ['created_at', 'is_active']

class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'avatar_url',
            'bio',
            'telefone',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'criado_em',
            'atualizado_em',
            'consentimento_dados'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']
    
    def get_avatar_url(self, obj):
        """Retorna a URL completa da avatar"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_ID = serializers.CharField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'product_ID',
            'product',
            'quantidade',
            'preco_no_momento',
            'adicionado_em',
            'atualizado_em'
        ]
        read_only_fields = ['produto', 'preco_no_momento', 'adicionado_em', 'atualizado_em']

class CartSerializer(serializers.ModelSerializer):
    itens = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'user',
            'itens',
            'total_itens',
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = ['user', 'total_itens', 'criado_em', 'atualizado_em']


class PriceHistoryDetailSerializer(serializers.ModelSerializer):
    """Serializador expandido para PriceHistory com mais detalhes"""
    class Meta:
        model = PriceHistory
        fields = [
            'id',
            'date',
            'price',
            'store',
            'is_lowest',
            'is_highest',
            'product_ID'
        ]
        read_only_fields = ['id', 'date', 'price', 'store', 'is_lowest', 'is_highest']


class ProductVariantSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'store_name',
            'variant_name',
            'price',
            'is_available',
            'last_price_check',
            'product_details'
        ]
        read_only_fields = ['id', 'last_price_check']


class ProductGroupSerializer(serializers.ModelSerializer):
    """Serializador para grupos de produtos deduplilicados"""
    variants = ProductVariantSerializer(many=True, read_only=True)
    canonical_product_details = ProductSerializer(source='canonical_product', read_only=True)
    
    class Meta:
        model = ProductGroup
        fields = [
            'id',
            'canonical_name',
            'canonical_product',
            'canonical_product_details',
            'lowest_price',
            'highest_price',
            'average_price',
            'variant_count',
            'variants',
            'last_updated',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'lowest_price',
            'highest_price',
            'average_price',
            'variant_count',
            'last_updated',
            'created_at'
        ]


class ProductGroupDetailSerializer(ProductGroupSerializer):
    """Serializador expandido com histórico de preços"""
    price_history = serializers.SerializerMethodField()
    
    def get_price_history(self, obj):
        """Retorna os últimos 360 pontos de histórico de preços"""
        history = obj.price_history.all()[:360]
        return PriceHistoryDetailSerializer(history, many=True).data
    
    class Meta(ProductGroupSerializer.Meta):
        fields = ProductGroupSerializer.Meta.fields + ['price_history']