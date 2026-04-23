import os
import re
import time
import shutil
import random
import certifi
import urllib3
import requests
import subprocess
import pandas as pd
from datetime import datetime
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from jinja2 import Environment, FileSystemLoader
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
script_dir = os.path.dirname(os.path.realpath(__file__))

# Lista de User-Agents
user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Brave/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Brave/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Brave/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/85.0.4341.18",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/85.0.4341.18",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/85.0.4341.18",
]

# Configurações do Firefox
gecko_path = os.path.join(script_dir, "geckodriver.exe")

# Detectar caminho do Firefox automaticamente
firefox_paths = [
    r'C:\Program Files\Mozilla Firefox\firefox.exe',
    r'C:\Program Files\Waterfox\waterfox.exe',
    os.path.expandvars(r'%APPDATA%\Mozilla Firefox\firefox.exe'),
]

firefox_binary_path = None
for path in firefox_paths:
    if os.path.exists(path):
        firefox_binary_path = path
        break

firefox_options = Options()
if firefox_binary_path:
    firefox_options.binary_location = firefox_binary_path
    print(f"Firefox encontrado em: \033[94m{firefox_binary_path}\033[0m")
else:
    print("\033[93mAviso: Firefox não encontrado. Deixando Selenium procurar automaticamente...\033[0m")

firefox_options.add_argument("--headless")
firefox_options.set_preference("dom.webdriver.enabled", False)
firefox_options.set_preference("layout.css.devPixelsPerPx", "0.2")
firefox_options.set_preference("useAutomationExtension", False)

selected_user_agent = random.choice(user_agents)
print(f"Usando User-Agent: \033[92m{selected_user_agent}\033[0m")
firefox_options.set_preference("general.useragent.override", selected_user_agent)

# Inicializar o driver com tratamento de erro
try:
    if os.path.exists(gecko_path):
        service = Service(gecko_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)
    else:
        # Se geckodriver não existe no diretório local, deixar Selenium procurar no PATH
        driver = webdriver.Firefox(options=firefox_options)
    driver.set_window_size(1920, 6080)
except Exception as e:
    print(f"\033[91mErro ao inicializar Firefox: {e}\033[0m")
    print("\033[93mCertifique-se de que Firefox está instalado e que geckodriver está no PATH ou no mesmo diretório do script.\033[0m")
    raise

product_id_counter = 0

# Configurações da Awin
AWIN_OAUTH_TOKEN = "41cc956c-1fa2-440d-bbbe-132e5afad516"
AWIN_PUBLISHER_ID = "1861294"
AWIN_API_URL = "https://api.awin.com/publishers/{publisher_id}/deep-links"

def generate_awin_affiliate_link(product_url):
    """Gera um link de afiliado usando a API Link Builder da Awin."""
    headers = {
        "Authorization": f"Bearer {AWIN_OAUTH_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "publisherId": AWIN_PUBLISHER_ID,
        "url": product_url,
        "format": "txt",
    }

    try:
        response = requests.post(
            AWIN_API_URL.format(publisher_id=AWIN_PUBLISHER_ID),
            headers=headers,
            json=payload,
            verify=certifi.where()
        )
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao gerar link de afiliado: {e}")
        return product_url
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return product_url
def format_filter_path(filter_path):
    """Formata o caminho de filtros com cores ANSI para exibição bonita.
    
    Args:
        filter_path: lista com [menu, type_, filter_, subfilter_, sub_1, sub_2, ...]
    
    Returns:
        String formatada com cores: \\033[92mmenu\\033[0m > \\033[94mtype_\\033[0m > ...
    """
    colors = ['\033[92m', '\033[94m', '\033[96m', '\033[95m', '\033[93m', '\033[91m', '\033[36m']
    formatted_parts = []
    for i, item in enumerate(filter_path):
        color = colors[i % len(colors)]
        formatted_parts.append(f"{color}{item}\033[0m")
    return " > ".join(formatted_parts)

def create_dynamic_filter_dict(filter_path):
    """Cria dicionário dinâmico com colunas de filtros baseado na profundidade.
    
    Args:
        filter_path: lista com [menu, type_, filter_, subfilter_, sub_1, sub_2, ...]
    
    Returns:
        Dicionário com chaves dinâmicas: menu, type_, filter_, subfilter_, subfilter_4, subfilter_5, ...
        Com valores vazios ('') para níveis não utilizados.
    
    Exemplo:
        filter_path = ['computadores', 'componentes', 'cpu', 'AMD', 'Socket AM5']
        Retorna:
        {
            'menu': 'computadores',
            'type_': 'componentes',
            'filter_': 'cpu',
            'subfilter_': 'AMD',
        }
    """
    # Nomes padrão para os primeiros 4 níveis
    column_names = ['menu', 'type_', 'filter_', 'subfilter_']
    
    # Se houver mais de 4 níveis, adiciona subfilter_4, subfilter_5, ...
    for i in range(4, len(filter_path)):
        column_names.append(f'subfilter_{i}')
    
    filter_dict = {}
    for i, value in enumerate(filter_path):
        filter_dict[column_names[i]] = value
    
    return filter_dict

def standardize_dataframes(df_list):
    """Padroniza todos os DataFrames com as mesmas colunas.
    
    Garante que todos os DataFrames tenham as mesmas colunas na mesma ordem,
    preenchendo com '' (vazio) os valores faltantes para colunas que não existem
    em alguns DataFrames.
    
    Args:
        df_list: lista de DataFrames
    
    Returns:
        Lista de DataFrames padronizados
    """
    if not df_list:
        return df_list
    
    # Coletar todas as colunas únicas na ordem apropriada
    all_columns = []
    order = ['product_ID', 'name', 'price', 'rating', 'review_count', 'store', 
             'image_url', 'product_link', 'affiliate_link', 'menu', 'type_', 
             'filter_', 'subfilter_']
    
    # Adicionar colunas na ordem padrão
    for col in order:
        for df in df_list:
            if col in df.columns and col not in all_columns:
                all_columns.append(col)
    
    # Adicionar as colunas subfilter_N que podem existir
    for df in df_list:
        for col in df.columns:
            if col.startswith('subfilter_') and col not in all_columns:
                all_columns.append(col)
    
    # Adicionar any remaining columns
    for df in df_list:
        for col in df.columns:
            if col not in all_columns:
                all_columns.append(col)
    
    # Preencher DataFrames faltantes com '' (vazio)
    standardized_list = []
    for df in df_list:
        df_copy = df.copy()
        for col in all_columns:
            if col not in df_copy.columns:
                df_copy[col] = ''
        df_copy = df_copy[all_columns]  # Reorganizar colunas na ordem correta
        standardized_list.append(df_copy)
    
    return standardized_list

def get_amazon_cookies():
    session = requests.Session()
    response = session.get('https://www.amazon.com.br')
    return session.cookies.get_dict()

def scrape_amazon_category(url, filter_path):
    """Scrapa Amazon com suporte a hierarquia dinâmica de filtros.
    
    Args:
        url: URL da categoria
        filter_path: lista com [menu, type_, filter_, subfilter, sub_1, sub_2, ...]
    """
    cookies = get_amazon_cookies()
    driver.get("https://www.amazon.com.br")
    
    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})
    
    driver.get(url)
    time.sleep(3)
    
    products = []
    menu = filter_path[0]
    type_ = filter_path[1]
    filter_ = filter_path[2]
    subfilter_ = filter_path[3] if len(filter_path) > 3 else ''
    
    try:
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@data-action-type="DISMISS"]'))
            ).click()
        except:
            pass

        while True:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.s-result-item[data-component-type="s-search-result"]'))
            )

            items = driver.find_elements(By.CSS_SELECTOR, 'div.s-result-item[data-component-type="s-search-result"]')
            
            for item in items:
                try:
                    global product_id_counter
                    filter_dict = create_dynamic_filter_dict(filter_path)
                    product_data = {
                        'product_ID': product_id_counter,
                        'name': item.find_element(By.CSS_SELECTOR, 'div[data-cy="title-recipe"] h2 span').text,
                        'price': 'Preço não disponível',
                        'rating': 'Avaliação não disponível',
                        'review_count': 'Contagem não disponível',
                        'store': 'Amazon',
                        'image_url': 'Imagem não disponível',
                        'product_link': '#',
                        'affiliate_link': '#',
                    }
                    product_data.update(filter_dict)
                    product_id_counter += 1
                    
                    try:
                        price_whole = item.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
                        price_decimal = item.find_element(By.CSS_SELECTOR, 'span.a-price-fraction').text
                        product_data['price'] = f"R$ {price_whole},{price_decimal.zfill(2)}"
                    except NoSuchElementException:
                        pass

                    try:
                        product_data['rating'] = item.find_element(By.CSS_SELECTOR, 'span.a-icon-alt').get_attribute('innerHTML').split()[0]
                    except NoSuchElementException:
                        pass

                    try:
                        product_data['review_count'] = item.find_element(By.CSS_SELECTOR, 'span.a-size-base.s-underline-text').text
                    except NoSuchElementException:
                        pass

                    try:
                        product_data['image_url'] = item.find_element(By.CSS_SELECTOR, 'img.s-image').get_attribute('src')
                    except NoSuchElementException:
                        pass

                    try:
                        product_link = item.find_element(By.CSS_SELECTOR, 'a.a-link-normal').get_attribute('href')
                        product_data['product_link'] = product_link
                        
                        if "/dp/" in product_link:
                            asin = product_link.split("/dp/")[1].split("/")[0]
                        elif "/gp/" in product_link:
                            asin = product_link.split("/gp/product/")[1].split("/")[0]
                        
                        if asin:
                            affiliate_id = "bragoon-20"
                            product_data['affiliate_link'] = f"https://www.amazon.com.br/dp/{asin}?tag={affiliate_id}"
                    except NoSuchElementException:
                        pass

                    products.append(product_data)

                except Exception as e:
                    print(f"\033[91mErro ao coletar produto: {e}\033[0m")
                    continue

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-next')
                if "disabled" in next_btn.get_attribute("class"):
                    break

                current_page = driver.find_element(By.CSS_SELECTOR, 'span.s-pagination-selected').text
                path_str = format_filter_path(filter_path)
                print(f"\033[93m Amazon\033[0m - Processando página \033[93m{current_page}\033[0m de {path_str}")

                driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                break

    except Exception as e:
        print(f"\033[1;91mErro principal: {str(e)}\033[0m")
    finally:
        path_str = format_filter_path(filter_path)
        print(f"Total coletado em {path_str}: \033[93m{len(products)}\033[0m")
    
    return pd.DataFrame(products)

def scrape_kabum_category(url, filter_path):
    """Scrapa Kabum com suporte a hierarquia dinâmica de filtros.
    
    Args:
        url: URL da categoria
        filter_path: lista com [menu, type_, filter_, subfilter, sub_1, sub_2, ...]
    """
    menu = filter_path[0]
    type_ = filter_path[1]
    filter_ = filter_path[2]
    subfilter_ = filter_path[3] if len(filter_path) > 3 else ''
    
    driver.get(url)
    time.sleep(3)
    
    products = []    
    try:
        page_count = 0
        while True:
            page_count += 1
            path_str = format_filter_path(filter_path)
            print(f"\033[93m Kabum\033[0m - Processando página \033[93m{page_count}\033[0m de {path_str}")
            
            # Esperar o carregamento dos elementos
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//img[contains(@src, "kabum.com.br/produtos")]'))
                )
            except:
                print(f"\033[93m⚠️  Timeout ao aguardar imagens de produtos\033[0m")
            
            items = []
            try:
                # Estratégia 1: Procurar as imagens de produtos (mais robusto)
                img_elements = driver.find_elements(By.XPATH, '//img[contains(@src, "kabum.com.br/produtos")]')
                
                if img_elements:
                    # Procurar por divs pais que contêm essas imagens - usar ancestor::div[5] que é o melhor container
                    seen_containers = set()
                    for img in img_elements:
                        try:
                            # ancestor::div[5] é geralmente a melhor escolha para o container do produto
                            container = img.find_element(By.XPATH, "ancestor::div[5]")
                            container_id = id(container)
                            if container_id not in seen_containers:
                                items.append(container)
                                seen_containers.add(container_id)
                        except:
                            pass
                
                # Estratégia 2: Fallback para div com múltiplas classes (estrutura TailwindCSS)
                if not items:
                    items = driver.find_elements(By.XPATH, '//div[contains(@class, "group") and contains(@class, "flex") and .//img[contains(@src, "kabum.com.br/produtos")]]')
                
                # Estratégia 3: Estrutura antiga
                if not items:
                    items = driver.find_elements(By.CSS_SELECTOR, 'div.productCard')
                    
            except Exception as e:
                print(f"\033[93m⚠️  Erro ao buscar produtos: {e}\033[0m")
            
            if not items:
                print(f"\033[93m⚠️  Nenhum produto encontrado na página. Encerrando...\033[0m")
                break
            
            for item in items:
                try:
                    global product_id_counter
                    filter_dict = create_dynamic_filter_dict(filter_path)
                    product_data = {
                        'product_ID': product_id_counter,
                        'name': 'Produto sem nome',
                        'price': 'Preço não disponível',
                        'rating': 'Avaliação não disponível',
                        'review_count': 'Contagem não disponível',
                        'store': 'Kabum',
                        'image_url': 'Imagem não disponível',
                        'product_link': '#',
                        'affiliate_link': '#',
                    }
                    product_data.update(filter_dict)
                    product_id_counter += 1
                    
                    # NOME DO PRODUTO - Tentar nova estrutura primeiro
                    try:
                        # Primeira opção: span com classes específicas
                        name_elem = item.find_element(By.CSS_SELECTOR, 'span.text-ellipsis.line-clamp-2.break-normal')
                        name_text = name_elem.text.strip()
                        if name_text:
                            product_data['name'] = name_text
                    except NoSuchElementException:
                        try:
                            # Segunda opção: qualquer span com text-ellipsis
                            name_elem = item.find_element(By.CSS_SELECTOR, 'span.text-ellipsis')
                            name_text = name_elem.text.strip()
                            if name_text:
                                product_data['name'] = name_text
                        except NoSuchElementException:
                            try:
                                # Terceira opção: estrutura antiga
                                product_data['name'] = item.find_element(By.CSS_SELECTOR, 'span.nameCard').text
                            except NoSuchElementException:
                                pass

                    # PREÇO DO PRODUTO - Nova estrutura com spans
                    try:
                        # Procurar spans com a classe de preço
                        price_spans = item.find_elements(By.XPATH, './/span[@class="text-base font-semibold text-gray-800"]')
                        if len(price_spans) >= 2:
                            # O penúltimo são os 2 últimos: penúltimo é R$ e último é o valor
                            currency = price_spans[-2].text.strip()
                            value = price_spans[-1].text.strip()
                            if value and currency:
                                product_data['price'] = f"{currency} {value}"
                        else:
                            raise NoSuchElementException("Preço não encontrado com estrutura padrão")
                    except (NoSuchElementException, IndexError):
                        try:
                            # Fallback: procurar qualquer span com R$ ou valor de preço
                            price_elem = item.find_element(By.XPATH, './/span[contains(text(), "R$")]')
                            price_text = price_elem.text.strip()
                            if price_text:
                                product_data['price'] = price_text[:30]
                        except:
                            try:
                                # Estrutura muito antiga
                                price = item.find_element(By.CSS_SELECTOR, 'span.priceCard').text
                                product_data['price'] = price if price else 'Preço não disponível'
                            except NoSuchElementException:
                                pass

                    # RATING - Extração melhorada
                    try:
                        # Procurar span com classe de avaliação
                        rating_elem = item.find_element(By.XPATH, './/span[@class="text-xs text-gray-400 font-semibold"]')
                        rating_text = rating_elem.text.strip()
                        
                        # Extrair apenas o número (pode vir como "5.0", "4.5", etc)
                        rating_match = re.search(r'(\d+[\.,]\d+|\d+)', rating_text)
                        if rating_match:
                            rating_value = rating_match.group(1).replace(',', '.')
                            product_data['rating'] = rating_value
                    except NoSuchElementException:
                        # Fallback: procurar qualquer span que contenha avaliação
                        try:
                            all_spans = item.find_elements(By.XPATH, './/span')
                            for span in all_spans:
                                text = span.text.strip()
                                rating_match = re.search(r'^(\d+[\.,]\d+)$|^(\d+)$', text)
                                if rating_match:
                                    rating_value = (rating_match.group(1) or rating_match.group(2)).replace(',', '.')
                                    # Validar que é um número entre 0 e 5
                                    if float(rating_value) <= 5:
                                        product_data['rating'] = rating_value
                                        break
                        except:
                            pass

                    # IMAGEM - Procura a imagem do produto
                    try:
                        # Procurar imagem com width específico (mais robusto)
                        img = item.find_element(By.CSS_SELECTOR, 'img[width="162"]')
                        src = img.get_attribute('src')
                        if src and src.startswith('http'):
                            product_data['image_url'] = src
                    except NoSuchElementException:
                        try:
                            # Fallback: estrutura antiga
                            product_data['image_url'] = item.find_element(By.CSS_SELECTOR, 'img.imageCard').get_attribute('src')
                        except NoSuchElementException:
                            # Última opção: qualquer img dentro do container que venha do Kabum
                            try:
                                img_elem = item.find_element(By.XPATH, './/img[contains(@src, "kabum.com.br/produtos")]')
                                src = img_elem.get_attribute('src')
                                if src and src.startswith('http'):
                                    product_data['image_url'] = src
                            except:
                                pass
                    
                    # REVIEW COUNT - Procurar contagem de reviews/avaliações
                    try:
                        # Procurar por spans que possuem formato "(123)"
                        review_elem = item.find_element(By.XPATH, './/span[contains(text(), "(") and contains(text(), ")")]')
                        review_text = review_elem.text.strip()
                        # Extrair número entre parênteses
                        review_match = re.search(r'\((\d+)\)', review_text)
                        if review_match:
                            product_data['review_count'] = review_match.group(1)
                    except:
                        pass

                    # LINK DO PRODUTO - Estratégia melhorada
                    product_link_found = None
                    try:
                        # Primeira opção: procurar link com classe productLink (estrutura moderna)
                        try:
                            product_link = item.find_element(By.CSS_SELECTOR, 'a.productLink').get_attribute('href')
                            if product_link and product_link != '#':
                                product_link_found = product_link
                        except NoSuchElementException:
                            pass
                        
                        # Segunda opção: procurar por qualquer link dentro do container que aponta para /hardware/
                        if not product_link_found:
                            all_links = item.find_elements(By.XPATH, './/a[@href]')
                            
                            # Criterio 1: Link que contém /hardware/ mas não tem ? (parâmetros)
                            for link in all_links:
                                href = link.get_attribute('href')
                                if href and 'kabum.com.br/hardware/' in href and '?' not in href:
                                    product_link_found = href
                                    break
                            
                            # Criterio 2: Qualquer link válido do Kabum se não encontrou pelo critério 1
                            if not product_link_found:
                                for link in all_links:
                                    href = link.get_attribute('href')
                                    if href and 'kabum.com.br' in href and href != '#':
                                        product_link_found = href
                                        break
                        
                        # Terceira opção: data attributes (alguns sites)
                        if not product_link_found:
                            product_link_found = item.get_attribute('data-href') or item.get_attribute('data-url')
                        
                        # Atualizar dados com o link encontrado
                        if product_link_found and product_link_found != '#':
                            product_data['product_link'] = product_link_found
                            try:
                                product_data['affiliate_link'] = generate_awin_affiliate_link(product_link_found)
                            except Exception as awin_error:
                                # Se houver erro ao gerar affiliate link, apenas mantem o URL original
                                product_data['affiliate_link'] = product_link_found
                    except Exception as e:
                        # Se houver qualquer erro na extração de link, não interrompe o fluxo
                        pass

                    products.append(product_data)

                except Exception as e:
                    print(f"\033[91mErro ao coletar produto Kabum: {e}\033[0m")
                    continue

            try:
                # Tentar encontrar botão próxima página
                next_btn = None
                
                try:
                    # Procurar por a.nextLink (é um botão interativo, não um link com href)
                    next_btn = driver.find_element(By.CSS_SELECTOR, 'a.nextLink')
                    
                    # Verificar se está disabled (verificar atributo aria-disabled ou classe)
                    aria_disabled = next_btn.get_attribute('aria-disabled')
                    next_class = next_btn.get_attribute('class') or ""
                    
                    if aria_disabled == 'true' or 'disabled' in next_class:
                        print(f"\033[93m Fim da paginação atingido (botão desabilitado)\033[0m")
                        break
                    
                    # Verificar se o botão está visível
                    if not next_btn.is_displayed():
                        print(f"\033[93m Botão próxima não está visível. Fim da paginação.\033[0m")
                        break
                        
                except NoSuchElementException:
                    print(f"\033[93m Botão próxima não encontrado. Fim da paginação.\033[0m")
                    break
                
                # Se chegou aqui, botão existe e está habilitado
                print(f"\033[92m✓ Próximo botão encontrado, navegando...\033[0m")
                
                # Scroll para o botão (importante para visibilidade)
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", next_btn)
                time.sleep(0.3)
                
                # Clicar no botão - tentar múltiplas estratégias
                try:
                    # Estratégia 1: Click normal
                    next_btn.click()
                except:
                    try:
                        # Estratégia 2: Click via JavaScript
                        driver.execute_script("arguments[0].click();", next_btn)
                    except:
                        # Estratégia 3: Simular pressionar Enter
                        next_btn.send_keys(Keys.RETURN)
                
                # Esperar a página carregar - aguardar novas imagens aparecerem
                print(f"\033[93m Aguardando carregamento da próxima página...\033[0m")
                time.sleep(3)  # Pequeno delay para iniciar carregamento
                
                try:
                    # Esperar até 15 segundos pelas imagens aparecerem
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, '//img[contains(@src, "kabum.com.br/produtos")]'))
                    )
                    print(f"\033[92m✓ Próxima página carregada\033[0m")
                except:
                    print(f"\033[93m⚠️  Timeout ao aguardar página, continuando mesmo assim...\033[0m")
                
                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"\033[91m Erro na paginação: {e}\033[0m")
                break

    except Exception as e:
        print(f"\033[1;91mErro principal Kabum: {str(e)}\033[0m")
    finally:
        path_str = format_filter_path(filter_path)
        print(f"Total coletado em {path_str}: \033[93m{len(products)}\033[0m")
    
    return pd.DataFrame(products)

# Lista de URLs para cada categoria de produto na Amazon
amazon_categories = {
    "computadores": {
        "componentes": { 
            "cpu": "https://www.amazon.com.br/s?k=CPUs&i=computers&rh=n%3A16364803011%2Cp_n_feature_two_browse-bin%3A31249020011%257C33197136011%2Cp_n_feature_fourteen_browse-bin%3A16365488011%257C16365489011%2Cp_123%3A341127%257C368902&dc&c=ts&qid=1739821275&rnid=119962938011&ts_id=16364803011&xpid=uyTp3zELV_X77&ref=sr_pg_1",
            "placa_mae": "https://www.amazon.com.br/s?k=Placas-M%C3%A3e&i=computers&rh=n%3A16364815011%2Cp_123%3A219979%257C249156%257C3275935%257C358772%257C362090%257C378555%257C413739%257C679200&dc&c=ts&qid=1739821698&rnid=119962938011&ts_id=16364815011&xpid=VJzBpwEYNJk8t&ref=sr_pg_2",
            "gpu": "https://www.amazon.com.br/s?keywords=Placas+de+V%C3%ADdeo&i=computers&rh=n%3A16364811011%2Cp_n_feature_three_browse-bin%3A82321813011%257C82321815011%257C82321817011%257C82321819011%257C82321821011%257C82321823011&dc&c=ts&qid=1739465654&rnid=82321807011&ts_id=16364811011&ref=sr_nr_p_n_feature_three_browse-bin_6&ds=v1%3Ay746Ge9I81X7DFRyzI7QAAutfaqjTrrXoI%2BAw9gapJs",
            "ram": "https://www.amazon.com.br/s?k=memoria+ram&i=electronics&rh=n%3A16209062011%2Cp_123%3A111070%257C236718%257C244985%257C248671%257C255322%257C256147%257C262088%257C3370136%257C370757%257C490032%257C6037502%257C8165750&dc&pf_rd_i=20930509011&pf_rd_m=A1ZZFT5FULY4LN&pf_rd_p=0202f9cf-4742-41cc-89a9-14c5386eec25&pf_rd_r=ZVT7QT41D9AH9MZMJJK5&pf_rd_s=merchandised-search-4&pf_rd_t=101&qid=1739821800&rnid=119962938011&ref=sr_nr_p_123_13&ds=v1%3Ay746Ge9I81X7DFRyzI7QAAutfaqjTrrXoI%2BAw9gapJs",
            "hd_ssd": "https://www.amazon.com.br/s?keywords=Mem%C3%B3rias+e+Armazenamento+Internos&i=computers&rh=n%3A17028669011%2Cp_123%3A110452%257C120943%257C202186%257C224943%257C236718%257C244985%257C255322%257C256147%257C303719%257C338696%257C46655%257C5606%257C709805&dc&c=ts&qid=1739821935&rnid=119962938011&ts_id=17028669011&ref=sr_nr_p_123_13&ds=v1%3AMC3Zj1g%2BM%2BWDRwawXhCxk5unXF6%2FafSHYyyRrXKnR%2Bw",
            "fonte": "https://www.amazon.com.br/s?keywords=Fontes+de+Alimenta%C3%A7%C3%A3o+para+Computadores&i=computers&rh=n%3A16364806011%2Cp_n_feature_browse-bin%3A16365579011%257C16365580011%257C16365581011%257C16365582011%257C16365583011%257C16365584011%257C16365585011%257C16365586011&dc&c=ts&qid=1739895379&rnid=16365578011&ts_id=16364806011&ref=sr_nr_p_n_feature_browse-bin_1&ds=v1%3AnCsk57QTYUa2cKet5XfhqkH7SdHwujpCk0hgKZg4tKk",
        }
    }
}

# Lista de URLs para cada categoria de produto na Kabum
kabum_categories = {
    "computadores": {
        "componentes": {    
            "cpu": {
                "AMD gen 2-5": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiQU00Il19&sort=most_searched",
                "AMD gen 7-9": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiQU01Il19&sort=most_searched",
                "FM+": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiRk0yKyJdfQ==&sort=most_searched",
                "threadripper": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiV1JYOCIsInNUUjUiXX0=&sort=most_searched",
                "intel 1ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTYiXX0=&sort=most_searched",
                "Intel 2ª-3ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTUiXX0=&sort=most_searched",
                "Intel 4ª e 5ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTAiXX0=&sort=most_searched",
                "LGA 1157": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDE1NjciXX0=&sort=most_searched",
                "LGA 2011": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDIwMTEiXX0=&sort=most_searched",
                "LGA 4189": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDQxODkiXX0=&sort=most_searched",
                "LGA 4677": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDQ2NzciXX0=&sort=most_searched",
                "Intel 6ª-9ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTEiXX0=&sort=most_searched",
                "intel 10ª e 11ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDEyMDAiXX0=&sort=most_searched",
                "Intel 12ª-14ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDE3MDAiXX0=&sort=most_searched",
                "Intel core 2": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=120&facet_filters=eyJTb2NrZXQiOlsiTEdBIDE4NTEiXX0=&sort=most_searched",
            },
            "placa_mae":{
                "intel": "https://www.kabum.com.br/hardware/placas-mae/placa-mae-intel?page_number=1&page_size=120&facet_filters=&sort=most_searched",
                "amd": "https://www.kabum.com.br/hardware/placas-mae/placa-mae-amd?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            },
            "gpu": "https://www.kabum.com.br/hardware/placa-de-video-vga?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "ram": "https://www.kabum.com.br/hardware/memoria-ram?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "hd": "https://www.kabum.com.br/hardware/disco-rigido-hd?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "ssd": "https://www.kabum.com.br/hardware/ssd-2-5?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "fonte": "https://www.kabum.com.br/hardware/fontes?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "air_cooler": "https://www.kabum.com.br/hardware/coolers/air-cooler?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "water_cooler": "https://www.kabum.com.br/hardware/coolers/water-cooler?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "placa_som": "https://www.kabum.com.br/hardware/placas-interfaces/placa-de-som?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
        "desktop": {
            "desktop amd e intel": "https://www.kabum.com.br/computadores/pc/pc-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "desktop intel": "https://www.kabum.com.br/computadores/pc/computador-intel?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "desktop amd": "https://www.kabum.com.br/computadores/pc/computador-amd?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "mini pc": "https://www.kabum.com.br/computadores/pc/computador-mini-pc?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "IMAC": "https://www.kabum.com.br/computadores/pc/computador-imac?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "MAC mini": "https://www.kabum.com.br/computadores/pc/computador-mac-mini?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "all-in-one": "https://www.kabum.com.br/computadores/pc/all-in-one?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
        "Notebook": {
            "Escritório": "https://www.kabum.com.br/computadores/notebooks/notebook-office?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Gamer": "https://www.kabum.com.br/computadores/notebooks/notebook-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "MacBook": "https://www.kabum.com.br/computadores/notebooks/macbook?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "ChromeBook": "https://www.kabum.com.br/computadores/notebooks/chromebook?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Acer": "https://www.kabum.com.br/computadores/notebooks/notebook-acer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Asus": "https://www.kabum.com.br/computadores/notebooks/notebook-asus?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Dell": "https://www.kabum.com.br/computadores/notebooks/notebook-dell?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Lenovo": "https://www.kabum.com.br/computadores/notebooks/notebook-lenovo?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "MSI": "https://www.kabum.com.br/computadores/notebooks/notebook-msi?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Multi": "https://www.kabum.com.br/computadores/notebooks/notebook-multilaser?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Positivo": "https://www.kabum.com.br/computadores/notebooks/notebook-positivo?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
        "perifericos": {
            "Streamer": "https://www.kabum.com.br/perifericos/streamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Carteira de Criptomoedas": "https://www.kabum.com.br/perifericos/carteira-de-criptomoedas?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Caixa de Som": "https://www.kabum.com.br/perifericos/caixa-de-som?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Headsets": "https://www.kabum.com.br/perifericos/headsets?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Webcam e Videoconferência": "https://www.kabum.com.br/perifericos/webcam-e-videoconferencia?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Mouse Pad": "https://www.kabum.com.br/perifericos/mouse-pad?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Óculos": "https://www.kabum.com.br/perifericos/oculos?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Cabos e Adaptadores": "https://www.kabum.com.br/perifericos/cabos-adaptadores?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Fone de Ouvido Gamer": "https://www.kabum.com.br/perifericos/fone-de-ouvido-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Teclado Gamer": "https://www.kabum.com.br/perifericos/teclado-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Mouse Gamer": "https://www.kabum.com.br/perifericos/-mouse-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Kit Gamer": "https://www.kabum.com.br/perifericos/kit-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Headset Gamer": "https://www.kabum.com.br/perifericos/headset-gamer?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Mesa Digitalizadora": "https://www.kabum.com.br/perifericos/mesa-digitalizadora?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Pen Drive": "https://www.kabum.com.br/perifericos/pen-drive?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Gabinetes": "https://www.kabum.com.br/perifericos/gabinetes?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Teclado e Mouse": "https://www.kabum.com.br/perifericos/teclado-mouse?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Suportes": "https://www.kabum.com.br/perifericos/suportes?page_number=1&page_size=120&facet_filters=&sort=most_searched"
        },
    },
    "videogame": {
        "playstation": {
            "consoles": "https://www.kabum.com.br/gamer/playstation/consoles-playstation?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "controles": "https://www.kabum.com.br/gamer/playstation/controles-playstation?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "perifiericos": "https://www.kabum.com.br/gamer/playstation/acessorios-playstation?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
        "nintendo": {
            "consoles": "https://www.kabum.com.br/gamer/nintendo/consoles-nintendo?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "controles": "https://www.kabum.com.br/gamer/nintendo/controles-nintendo?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "perifiericos": "https://www.kabum.com.br/gamer/nintendo/acessorios-nintendo?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
        "xbox": {
            "consoles": "https://www.kabum.com.br/gamer/xbox/consoles-xbox?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "controles": "https://www.kabum.com.br/gamer/xbox/controles-xbox?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "perifiericos": "https://www.kabum.com.br/gamer/xbox/acessorios-xbox?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
    },
    "simuladores": {
        "racing": {
            "volantes e pedais": "https://www.kabum.com.br/gamer/simuladores/racing/volantes-e-pedais?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "cambios e alavancas": "https://www.kabum.com.br/gamer/simuladores/racing/cambios-e-alavancas?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "cockpits e suportes": "https://www.kabum.com.br/gamer/simuladores/racing/cockpits-e-suportes?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "acessorios": "https://www.kabum.com.br/gamer/simuladores/racing/acessorios?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
        "fly-simulator": {
            "Alavancas e Manetes": "https://www.kabum.com.br/gamer/simuladores/fly-simulator/alavancas-e-manetes?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Controladores de Manche": "https://www.kabum.com.br/gamer/simuladores/fly-simulator/controladores-de-manche?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Pedais": "https://www.kabum.com.br/gamer/simuladores/fly-simulator/pedais?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Instrumentos": "https://www.kabum.com.br/gamer/simuladores/fly-simulator/instrumentos?page_number=1&page_size=120&facet_filters=&sort=most_searched",
            "Cockpits e Suportes": "https://www.kabum.com.br/gamer/simuladores/fly-simulator/cockpits-e-suportes?page_number=1&page_size=120&facet_filters=&sort=most_searched",
        },
    },
}

def scrape_all_categories():
    all_products = []
    
    def process_categories_recursive(categories, path, scrape_func, source_name):
        """Processa categorias recursivamente em qualquer profundidade.
        
        Args:
            categories: dicionário de categorias
            path: lista com o caminho até agora [menu, type_, filter_, subfilter_, ...]
            scrape_func: função de scraping (scrape_amazon_category ou scrape_kabum_category)
            source_name: nome da fonte ('amazon' ou 'Kabum')
        """
        for key, value in categories.items():
            new_path = path + [key]
            
            if isinstance(value, dict):
                # Se é dicionário, desce recursivamente mais um nível
                process_categories_recursive(value, new_path, scrape_func, source_name)
            else:
                # Se é string (URL), faz o scraping
                path_str = format_filter_path(new_path)
                print(f"Scraping {source_name}: {path_str}")
                df = scrape_func(value, new_path)
                all_products.append(df)


            # Obtém a data e hora atual
    horainicial = datetime.now()

        # Formata apenas para hora:minuto:segundo
    horainicio = horainicial.strftime("%H:%M:%S")

    print(f"Hora início: {horainicio} ")

    try:
        # Scraping Amazon
        for menu, categories in amazon_categories.items():
            process_categories_recursive(categories, [menu], scrape_amazon_category, 'amazon')
    except KeyboardInterrupt:
        pass

    try:    
        # Scraping Kabum
        for menu, categories in kabum_categories.items():
            process_categories_recursive(categories, [menu], scrape_kabum_category, 'Kabum')
    except KeyboardInterrupt:
        pass    
    except Exception as e:
        print(f"\033[91mErro geral durante scraping Kabum: {e}\033[0m")
        pass
    horafinal = datetime.now()

        # Formata apenas para hora:minuto:segundo
    horafim = horafinal.strftime("%H:%M:%S")
    # Combinar todos os DataFrames


    if all_products:
        # Padronizar DataFrames para garantir mesmas colunas
        all_products = standardize_dataframes(all_products)
        final_df = pd.concat(all_products, ignore_index=True)
        
        # Criar pasta output se não existir
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar em XLSX (para a pipeline)
        try:
            xlsx_path = os.path.join(output_dir, 'produtos.xlsx')
            final_df.to_excel(xlsx_path, index=False, engine='openpyxl')
            print(f"✅ \033[92mDados salvos em: {xlsx_path}\033[0m")
        except ImportError:
            print("\033[91m❌ Erro: openpyxl não está instalado. Execute: pip install openpyxl\033[0m")
        except Exception as e:
            print(f"\033[91m❌ Erro ao salvar XLSX: {e}\033[0m")
        
        # Salvar também em CSV (compatibilidade)
        try:
            csv_path = '../bragoon-ecommerce/backend/produtos.csv'
            final_df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"✅ \033[92mDados salvos em: {csv_path}\033[0m")
        except Exception as e:
            print(f"\033[91m❌ Erro ao salvar CSV: {e}\033[0m")
        
    else:
        print("\033[93m⚠️  Nenhum produto foi coletado.\033[0m")

    print(f"Hora início: {horainicio} | Hora fim: {horafim}")

if __name__ == "__main__":
    try:
        scrape_all_categories()
    finally:
        driver.quit()