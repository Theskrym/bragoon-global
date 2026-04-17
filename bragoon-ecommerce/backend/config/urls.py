from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from products import views
from products.auth_views import LoginView, RegisterView, UserViewSet

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'alerts', views.AlertViewSet, basename='alert')
router.register(r'carrinho', views.CartViewSet, basename='carrinho')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/products/<str:product_id>/price-history/', views.PriceHistoryView.as_view(), name='price-history'),
    
    # Authentication Routes
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/user/me/', UserViewSet.as_view(), name='user-profile'),
    
    # Profile endpoint
    path('api/perfil/', views.UserProfileView.as_view(), name='user-profile-detail'),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)