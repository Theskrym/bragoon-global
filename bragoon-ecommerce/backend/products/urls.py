from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'alerts', views.AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<str:product_id>/price-history/', views.PriceHistoryView.as_view(), name='price-history'),
]