from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    triggered_at = models.DateTimeField(null=True, blank=True, help_text="Quando o alerta foi disparado")
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class ProductGroup(models.Model):
    """
    Agrupa produtos que são o mesmo item (mesmas especificações).
    Exemplo: Ryzen 5 5500 de diferentes lojas = 1 ProductGroup
    """
    canonical_name = models.CharField(max_length=500, unique=True, db_index=True, help_text="Nome canônico do produto (sem loja, preço, etc)")
    canonical_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_canonical', help_text="Produto com menor preço do grupo")
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Preço mais baixo atual do grupo")
    highest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Preço mais alto atual do grupo")
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Preço médio do grupo")
    variant_count = models.IntegerField(default=0, help_text="Quantidade de variantes (lojas) deste produto")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Grupo de Produtos"
        verbose_name_plural = "Grupos de Produtos"
        ordering = ['-last_updated']
    
    def __str__(self):
        return self.canonical_name


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='price_history', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    store = models.CharField(max_length=100, blank=True, help_text="Loja onde foi registrado o preço")
    is_lowest = models.BooleanField(default=False, help_text="Era o preço mais baixo no grupo naquela data")
    is_highest = models.BooleanField(default=False, help_text="Era o preço mais alto no grupo naquela data")
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['group', '-date']),
            models.Index(fields=['product', '-date']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - R$ {self.price} em {self.date.date()}"

class ProductVariant(models.Model):
    """
    Variante de um produto dentro de um grupo.
    Diferentes lojas vendendo o mesmo produto = diferentes variantes.
    """
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='variants')
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='variant_info')
    store_name = models.CharField(max_length=100)
    variant_name = models.CharField(max_length=200, blank=True, help_text="Nome específico da variante (cor, tamanho, etc)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_price_check = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['group', 'store_name']
        ordering = ['price']
    
    def __str__(self):
        return f"{self.group.canonical_name} - {self.store_name}"

class UserProfile(models.Model):
    """
    Perfil de usuário com conformidade LGPD e ISO 27001.
    LGPD Compliance:
    - criado_em: Data de criação da conta (direito à portabilidade)
    - atualizado_em: Timestamp de última atualização
    - consentimento_dados: Consentimento para armazenamento de dados
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    
    # LGPD Compliance
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    consentimento_dados = models.BooleanField(default=True, help_text="Consentimento para armazenamento de dados pessoais")
    data_consentimento = models.DateTimeField(auto_now_add=True, help_text="Data e hora do consentimento")
    
    # ISO 27001 - Auditoria
    data_acesso_ultima = models.DateTimeField(null=True, blank=True, help_text="Última vez que o perfil foi acessado")
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

class Cart(models.Model):
    """
    Carrinho de compras persistente por usuário.
    Um carrinho por usuário, atualizado ao adicionar/remover produtos.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    total_itens = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Carrinho de Compras"
        verbose_name_plural = "Carrinhos de Compras"
    
    def __str__(self):
        return f"Carrinho de {self.user.username} ({self.total_itens} itens)"

class CartItem(models.Model):
    """
    Itens individuais do carrinho de compras.
    Cada item vinculado a um carrinho e um produto.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='itens')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_no_momento = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço quando o item foi adicionado")
    adicionado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product']
        verbose_name = "Item do Carrinho"
        verbose_name_plural = "Itens do Carrinho"
    
    def __str__(self):
        return f"{self.product.name} x{self.quantidade}"

class SyncLog(models.Model):
    """
    Registro de sincronizações do scraper.
    Rastreia quando os produtos foram atualizados pela última vez.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    produtos_atualizados = models.IntegerField(default=0, help_text="Quantidade de produtos atualizados nesta sincronização")
    status = models.CharField(max_length=20, choices=[
        ('success', 'Sucesso'),
        ('error', 'Erro'),
        ('partial', 'Parcial')
    ], default='success')
    detalhes = models.TextField(blank=True, null=True, help_text="Detalhes da sincronização")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Sincronização"
        verbose_name_plural = "Registros de Sincronização"
    
    def __str__(self):
        return f"Sincronização em {self.timestamp} - {self.status}"