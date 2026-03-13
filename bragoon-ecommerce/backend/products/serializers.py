from rest_framework import serializers
from .models import Product, PriceHistory, Alert

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