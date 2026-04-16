from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from products import views
from products.auth_views import LoginView, RegisterView, UserViewSet

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'alerts', views.AlertViewSet, basename='alert')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/products/<str:product_id>/price-history/', views.PriceHistoryView.as_view(), name='price-history'),
    
    # Authentication Routes
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/user/me/', UserViewSet.as_view(), name='user-profile'),
]