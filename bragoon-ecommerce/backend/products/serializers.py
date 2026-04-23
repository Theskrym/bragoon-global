from rest_framework import serializers
from .models import Product, PriceHistory, Alert, UserProfile, Cart, CartItem, ProductGroup, ProductVariant, PriceSnapshot

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


# ===============================
# PRODUCT GROUPS SERIALIZERS
# ===============================

class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer para variantes individuais de um produto"""
    class Meta:
        model = ProductVariant
        fields = [
            'variant_id',
            'loja',
            'preco_atual',
            'preco_anterior',
            'link_produto',
            'link_afiliado',
            'imagem_url',
            'rating',
            'review_count',
            'disponivel',
            'estoque',
            'posicao_ranking'
        ]
        read_only_fields = ['variant_id']


class PriceSnapshotSerializer(serializers.ModelSerializer):
    """Serializer para snapshots históricos de preço"""
    class Meta:
        model = PriceSnapshot
        fields = [
            'snapshot_id',
            'data',
            'preco_minimo',
            'preco_maximo',
            'preco_medio',
            'total_variantes'
        ]
        read_only_fields = ['snapshot_id']


class ProductGroupSerializer(serializers.ModelSerializer):
    """Serializer básico para listar grupos de produtos"""
    class Meta:
        model = ProductGroup
        fields = [
            'product_group_id',
            'canonical_name',
            'category',
            'image_url',
            'min_price',
            'max_price',
            'avg_price',
            'total_variantes'
        ]
        read_only_fields = [
            'product_group_id',
            'min_price',
            'max_price',
            'avg_price',
            'total_variantes'
        ]


class ProductGroupDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para um grupo específico (com variantes e histórico)"""
    variantes = ProductVariantSerializer(many=True, read_only=True)
    price_snapshots = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductGroup
        fields = [
            'product_group_id',
            'canonical_name',
            'category',
            'image_url',
            'min_price',
            'max_price',
            'avg_price',
            'total_variantes',
            'variantes',
            'price_snapshots',
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = [
            'product_group_id',
            'min_price',
            'max_price',
            'avg_price',
            'total_variantes',
            'criado_em',
            'atualizado_em'
        ]
    
    def get_price_snapshots(self, obj):
        """Retorna últimos 360 snapshots de preço (1 ano de dados)"""
        snapshots = obj.price_snapshots.all()[:360]
        return PriceSnapshotSerializer(snapshots, many=True).data