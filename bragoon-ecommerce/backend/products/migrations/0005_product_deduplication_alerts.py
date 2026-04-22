# Generated migration for product deduplication and alerts system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_synclog'),
    ]

    operations = [
        # Criar ProductGroup primeiro (sem dependências)
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canonical_name', models.CharField(db_index=True, help_text='Nome canônico do produto (sem loja, preço, etc)', max_length=500, unique=True)),
                ('lowest_price', models.DecimalField(decimal_places=2, default=0, help_text='Preço mais baixo atual do grupo', max_digits=10)),
                ('highest_price', models.DecimalField(decimal_places=2, default=0, help_text='Preço mais alto atual do grupo', max_digits=10)),
                ('average_price', models.DecimalField(decimal_places=2, default=0, help_text='Preço médio do grupo', max_digits=10)),
                ('variant_count', models.IntegerField(default=0, help_text='Quantidade de variantes (lojas) deste produto')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('canonical_product', models.ForeignKey(blank=True, help_text='Produto com menor preço do grupo', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_canonical', to='products.product')),
            ],
            options={
                'verbose_name': 'Grupo de Produtos',
                'verbose_name_plural': 'Grupos de Produtos',
                'ordering': ['-last_updated'],
            },
        ),
        
        # Criar ProductVariant (depende de ProductGroup)
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=100)),
                ('variant_name', models.CharField(blank=True, help_text='Nome específico da variante (cor, tamanho, etc)', max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('last_price_check', models.DateTimeField(auto_now=True)),
                ('is_available', models.BooleanField(default=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.productgroup')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='variant_info', to='products.product')),
            ],
            options={
                'ordering': ['price'],
            },
        ),
        
        # Adicionar campo triggered_at ao Alert
        migrations.AddField(
            model_name='alert',
            name='triggered_at',
            field=models.DateTimeField(blank=True, help_text='Quando o alerta foi disparado', null=True),
        ),
        
        # Alterar PriceHistory - adicionar campos
        migrations.AddField(
            model_name='pricehistory',
            name='store',
            field=models.CharField(blank=True, help_text='Loja onde foi registrado o preço', max_length=100),
        ),
        migrations.AddField(
            model_name='pricehistory',
            name='is_lowest',
            field=models.BooleanField(default=False, help_text='Era o preço mais baixo no grupo naquela data'),
        ),
        migrations.AddField(
            model_name='pricehistory',
            name='is_highest',
            field=models.BooleanField(default=False, help_text='Era o preço mais alto no grupo naquela data'),
        ),
        migrations.AddField(
            model_name='pricehistory',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='price_history', to='products.productgroup'),
        ),
        
        # Alterar campo date de PriceHistory
        migrations.AlterField(
            model_name='pricehistory',
            name='date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        
        # Adicionar índices para PriceHistory
        migrations.AddIndex(
            model_name='pricehistory',
            index=models.Index(fields=['group', '-date'], name='price_hist_group_date'),
        ),
        migrations.AddIndex(
            model_name='pricehistory',
            index=models.Index(fields=['product', '-date'], name='price_hist_product_date'),
        ),
        
        # Adicionar constraint única para ProductVariant
        migrations.AddConstraint(
            model_name='productvariant',
            constraint=models.UniqueConstraint(fields=['group', 'store_name'], name='unique_group_store'),
        ),
    ]
