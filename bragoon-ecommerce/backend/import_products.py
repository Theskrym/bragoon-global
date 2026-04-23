import os
import sys
import csv
import django
from django.db import transaction
from products.models import Product

# Configuração do Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def convert_br_number(number_str):
    """Converte números no formato brasileiro (1.234,56) para float"""
    if not number_str or not isinstance(number_str, str):
        return 0.0
    cleaned = number_str.replace('.', '').replace(',', '.').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def convert_review_count(count_str):
    """Converte o número de reviews (pode conter ponto como separador de milhar)"""
    if not count_str:
        return 0
    try:
        return int(count_str.replace('.', ''))
    except ValueError:
        return 0

def process_batch(batch):
    """Processa um lote de produtos de uma vez"""
    products_to_create = []
    products_to_update = []
    
    # Verifica quais produtos já existem
    existing_ids = set(Product.objects.filter(
        product_ID__in=[p['product_ID'] for p in batch]
    ).values_list('product_ID', flat=True))
    
    for row in batch:
        try:
            # Converter os valores
            price = convert_br_number(row['price'].replace('R$', '').strip())
            rating_str = row['rating'].split('/')[0] if '/' in row['rating'] else row['rating']
            rating = convert_br_number(rating_str.strip())
            review_count = convert_review_count(row['review_count'])
            
            product_data = {
                'name': row['name'],
                'price': price,
                'rating': rating,
                'review_count': review_count,
                'store': row['store'],
                'image_url': row['image_url'],
                'product_link': row['product_link'],
                'affiliate_link': row['affiliate_link'],
                'menu': row['menu'],
                'type': row['type'],
                'filter': row.get('filter', ''),
                'subfilter': row.get('subfilter', '')
            }
            
            if row['product_ID'] in existing_ids:
                # Para atualização
                products_to_update.append((row['product_ID'], product_data))
            else:
                # Para criação
                products_to_create.append(Product(
                    product_ID=row['product_ID'],
                    **product_data
                ))
                
        except Exception as e:
            print(f"Erro ao processar produto {row.get('product_ID', '')}: {str(e)}")
            continue
    
    # Processa em transação única
    with transaction.atomic():
        # Cria novos produtos em lote
        if products_to_create:
            Product.objects.bulk_create(products_to_create)
            print(f"Criados {len(products_to_create)} novos produtos")
        
        # Atualiza produtos existentes em lote
        if products_to_update:
            for product_id, data in products_to_update:
                Product.objects.filter(product_ID=product_id).update(**data)
            print(f"Atualizados {len(products_to_update)} produtos existentes")

def run():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'products.csv')
    batch_size = 10000  # Ajuste conforme necessário
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        batch = []
        count = 0
        
        for row in reader:
            if row is None:
                continue
            # Remover espaços dos nomes das colunas
            row = {key.strip(): (value.strip() if isinstance(value, str) else value) for key, value in row.items() if key}
            
            batch.append(row)
            count += 1
            
            if len(batch) >= batch_size:
                print(f"Processando batch de {len(batch)} produtos...")
                process_batch(batch)
                batch = []
        
        # Processa último batch
        if batch:
            print("Processando último batch...")
            process_batch(batch)
    
    
    print("Importação concluída com sucesso!")

if __name__ == '__main__':
    run()