import os
import time
import subprocess
import pandas as pd
import shutil
from jinja2 import Environment, FileSystemLoader

def update_html_from_excel(excel_file, output_html):
    # Lê o arquivo Excel
    df = pd.read_excel(excel_file)

    csv_path = os.path.splitext(excel_file)[0] + '.csv'
    df.to_csv(csv_path, index=False)
    print(f'Arquivo CSV salvo em: {csv_path}')
    
    
    # Configura o ambiente Jinja2 com caminho relativo ao script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    templates_dir = os.path.join(script_dir, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('template.html')

    def dummy_url_for(endpoint, **kwargs):
        if endpoint == 'product_detail':
            product_name = kwargs.get('product_name', '').replace(' ', '_')
            return f"/produto/{product_name}.html"
        return "#"

    def generate_product_url(product_name):
        return f"/produto/{product_name.replace(' ', '_')}.html"

    # Injeta as funções no template
    env.globals.update(
        url_for=dummy_url_for,
        generate_product_url=generate_product_url
    )
    env.globals.update(url_for=dummy_url_for)  # Injeta a função no template

    # Renderiza o template com os dados do DataFrame
    html_content = template.render(products=df.to_dict(orient='records'))

    # Salva o conteúdo HTML em um arquivo
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)   
        
def update_static_files(output_path):
    # Copia os arquivos CSS e JS para a pasta de saída
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    static_css_path = os.path.join(script_dir, 'static', 'style.css')
    output_css_path = os.path.join(output_path, 'style.css')
    shutil.copy(static_css_path, output_css_path)

    static_js_path = os.path.join(script_dir, 'static', 'scripts.js')
    output_js_path = os.path.join(output_path, 'scripts.js')
    shutil.copy(static_js_path, output_js_path)
    
def executar_comandos_git():
    # Caminho para a pasta output (relativo ao script, funciona em qualquer computador)
    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')

    # Comandos que você deseja executar no CMD
    commands = [
        f'cd /d "{output_dir}"',  # Navega até a pasta output
        'git status',  # Verifica o status do repositório
        'git add .',  # Adiciona todos os arquivos da pasta output ao staging area
        'git commit -m "Atualização automática"',  # Faz o commit das alterações locais
        'git push origin main',  # Faz o push para o repositório remoto
        'git remote -v'
    ]

    # Junta os comandos em um único comando para o CMD
    cmd_command = " & ".join(commands)

    # Executa os comandos em uma única sessão do CMD
    result = subprocess.run(cmd_command, shell=True, text=True, capture_output=True)

    # Verifica se houve erro
    if result.returncode != 0:
        print(f"Erro ao executar comandos Git: {result.stderr}")
    else:
        print("Comandos Git executados com sucesso.")


if __name__ == "__main__":
    # Caminho relativo ao script (funciona em qualquer computador)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(script_dir, 'output')
    excel_file = os.path.join(output_path, 'produtos.xlsx')
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    update_html_from_excel(excel_file, os.path.join(output_path, 'index.html'))
    update_static_files(output_path)
    time.sleep(2)
    executar_comandos_git() 