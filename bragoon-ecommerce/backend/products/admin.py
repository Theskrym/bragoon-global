from django.contrib import admin
from .models import Product, PriceHistory, Alert, UserProfile, Cart, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'name', 'price', 'store', 'rating')
    search_fields = ('name', 'product_ID', 'store')
    list_filter = ('store', 'menu', 'type')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'date')
    list_filter = ('date', 'product')
    search_fields = ('product__name',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'target_price', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'product__name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'criado_em', 'consentimento_dados')
    list_filter = ('criado_em', 'consentimento_dados')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('criado_em', 'atualizado_em', 'data_consentimento')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('adicionado_em', 'atualizado_em')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_itens', 'criado_em', 'atualizado_em')
    list_filter = ('criado_em', 'atualizado_em')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantidade', 'adicionado_em')
    list_filter = ('adicionado_em', 'cart__user')
    search_fields = ('product__name', 'cart__user__email')
    readonly_fields = ('adicionado_em', 'atualizado_em')
