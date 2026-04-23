from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from products.models import Alert, ProductVariant, PriceSnapshot, Product
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica alertas de preço e notifica usuários quando o alvo é atingido'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando alertas de preço...'))
        
        # Obter alertas ativos
        alerts = Alert.objects.filter(is_active=True)
        
        if not alerts.exists():
            self.stdout.write(self.style.WARNING('⚠️  Nenhum alerta ativo encontrado'))
            return
        
        self.stdout.write(f'📋 Verificando {alerts.count()} alertas ativos...')
        
        alerts_triggered = 0
        
        for alert in alerts:
            product = alert.product
            target_price = float(alert.target_price)
            current_price = float(product.price)
            
            # Verificar condição do alerta
            should_trigger = False
            
            if alert.notification_type == 'price_below':
                # Alerta: preço está abaixo do alvo
                if current_price <= target_price:
                    should_trigger = True
            
            elif alert.notification_type == 'lowest_6_months':
                # Alerta: preço é o mais baixo em 6 meses
                snapshots = PriceSnapshot.objects.filter(
                    product_group__canonical_name=product.name
                ).order_by('-data')[:180]  # Últimos ~6 meses
                
                if snapshots.exists():
                    min_price_6m = min([float(s.preco_minimo) for s in snapshots])
                    if current_price <= min_price_6m:
                        should_trigger = True
            
            # Disparar alerta
            if should_trigger:
                self.trigger_alert(alert)
                alerts_triggered += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Alerta disparado: {product.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {alerts_triggered} alertas disparados!'))
    
    def trigger_alert(self, alert):
        """Dispara um alerta para o usuário"""
        product = alert.product
        
        # Aqui você pode implementar:
        # 1. Enviar email
        # 2. Enviar notificação push
        # 3. Salvar notificação no banco de dados
        # 4. Enviar para WebSocket
        
        message = f"🎉 Alerta de preço! {product.name} chegou em R$ {product.price}"
        
        logger.info(f"ALERT TRIGGERED: {message}")
        
        # Desativar alerta após disparar (opcional)
        # alert.is_active = False
        # alert.save()
