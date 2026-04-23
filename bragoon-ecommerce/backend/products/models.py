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


# ===============================
# DEDUPLICATION - PRODUCT GROUPS
# ===============================

class ProductGroup(models.Model):
    """
    Grupo de produtos deduplilicados (mesmo produto de diferentes lojas).
    Cada grupo contém várias ProductVariant (mesma CPU em Kabum, Pichau, etc).
    """
    product_group_id = models.AutoField(primary_key=True)
    canonical_name = models.CharField(max_length=300, db_index=True, help_text="Nome único do produto")
    category = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    
    # Preços agregados
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_variantes = models.IntegerField(default=0, help_text="Quantidade de variantes (lojas)")
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['canonical_name']
        indexes = [
            models.Index(fields=['canonical_name']),
            models.Index(fields=['category']),
            models.Index(fields=['min_price']),
        ]
        verbose_name = "Grupo de Produtos"
        verbose_name_plural = "Grupos de Produtos"
    
    def __str__(self):
        return f"{self.canonical_name} ({self.total_variantes} variantes)"


class ProductVariant(models.Model):
    """
    Variante individual de um produto (mesmo produto de diferentes lojas).
    Cada variante é um link único para um produto em uma loja específica.
    """
    variant_id = models.AutoField(primary_key=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='variantes')
    original_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='variant_info', null=True, blank=True)
    
    # Informações específicas da variante
    loja = models.CharField(max_length=100, db_index=True)
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2)
    preco_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    link_produto = models.URLField()
    link_afiliado = models.URLField(blank=True, null=True)
    imagem_url = models.URLField(blank=True, null=True)
    
    # Avaliações
    rating = models.FloatField(default=0)
    review_count = models.IntegerField(default=0)
    
    # Disponibilidade
    disponivel = models.BooleanField(default=True)
    estoque = models.CharField(max_length=50, blank=True, null=True)
    
    # Rastreamento
    posicao_ranking = models.IntegerField(default=999, help_text="Posição no ranking de preço (1 = mais barato)")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['preco_atual']
        unique_together = ['product_group', 'loja', 'link_produto']
        verbose_name = "Variante de Produto"
        verbose_name_plural = "Variantes de Produtos"
    
    def __str__(self):
        return f"{self.loja} - R$ {self.preco_atual}"


class PriceSnapshot(models.Model):
    """
    Snapshot histórico de preços para um ProductGroup.
    Armazena min/max/média diária (máximo 360 snapshots = 1 ano).
    """
    snapshot_id = models.AutoField(primary_key=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='price_snapshots')
    data = models.DateField(db_index=True)
    
    # Preços do dia
    preco_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_maximo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_medio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Metadata
    total_variantes = models.IntegerField(help_text="Quantidade de variantes neste dia")
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data']
        unique_together = ['product_group', 'data']
        verbose_name = "Snapshot de Preço"
        verbose_name_plural = "Snapshots de Preço"
    
    def __str__(self):
        return f"{self.product_group.canonical_name} - {self.data}"