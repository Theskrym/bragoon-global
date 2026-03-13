from flask import Flask, render_template
import pandas as pd
import os
from urllib.parse import quote

# Caminhos absolutos (garanta que está executando o server.py da pasta raiz)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
web_scrapper_dir = os.path.join(base_dir, 'web-scrapper')

app = Flask(
    __name__,
    template_folder=os.path.join(web_scrapper_dir, 'templates'),  # Mudança aqui
    static_url_path='/output'  # Adicionando esta linha
)

def load_products():
    # Caminho para o arquivo Excel
    products_path = os.path.join('web-scrapper', 'output', 'produtos.xlsx')
    df = pd.read_excel(products_path)
    products = df.to_dict('records')
    return products

# Função para gerar URLs de produtos
def generate_product_url(product_name):
    return f"/produto/{quote(product_name)}"

def generate_product_url(product_name):
    return f"/produto/{quote(str(product_name).encode('utf-8').decode('utf-8'))}"

@app.route('/')
def index():
    try:
        products = load_products()
        unique_products = {}
        for product in products:
            if product['name'] not in unique_products:
                unique_products[product['name']] = product
        
        # Primeiro renderiza o template e salva em produtos.html
        rendered_html = render_template(
            'template.html',  # usa o template base
            products=unique_products.values(),
            generate_product_url=lambda name: f'/produto/{quote(str(name).encode("utf-8").decode("utf-8"))}'
        )
        # Salva o HTML renderizado em output/produtos.html
        output_path = os.path.join(web_scrapper_dir, 'output', 'index.html')
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(rendered_html)
        
        return rendered_html
    except Exception as e:
        print(f"Erro: {e}")
        return str(e), 500

# Adicionar a função ao contexto do template
@app.context_processor
def inject_generate_product_url():
    return dict(generate_product_url=generate_product_url)

@app.route('/produto/<string:product_name>')
def product_detail(product_name):
    products = load_products()
    product_listings = [p for p in products if p['name'] == product_name]
    
    if not product_listings:
        return "Produto não encontrado", 404
    
    valid_prices = []
    for p in product_listings:
        try:
            price_str = p['price'].replace('R$ ', '').replace('.', '').replace(',', '.')
            valid_prices.append(float(price_str))
        except:
            continue
    
    min_price = f"R$ {min(valid_prices):,.2f}".replace('.', ',') if valid_prices else "Indisponível"
    
    return render_template('product_detail.html',
                         product=product_listings[0],
                         store_listings=product_listings,
                         min_price=min_price)

if __name__ == '__main__':
    app.run(debug=True)