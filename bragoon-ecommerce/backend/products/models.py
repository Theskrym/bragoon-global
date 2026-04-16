from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_ID = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    review_count = models.IntegerField()
    store = models.CharField(max_length=100)
    image_url = models.URLField()
    product_link = models.URLField()
    affiliate_link = models.URLField()
    menu = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    filter = models.CharField(max_length=100, blank=True, null=True)
    subfilter = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-date']

class Alert(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notification_type = models.CharField(max_length=50, choices=[
        ('price_below', 'Preço abaixo de'),
        ('lowest_6_months', 'Preço mais baixo em 6 meses')
    ])
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"