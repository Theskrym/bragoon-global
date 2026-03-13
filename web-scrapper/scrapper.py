import os
import time
import shutil
import random
import certifi
import urllib3
import requests
import subprocess
import pandas as pd
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
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

def get_amazon_cookies():
    session = requests.Session()
    response = session.get('https://www.amazon.com.br')
    return session.cookies.get_dict()

def scrape_amazon_category(url, menu, type_, filter_, subfilter_):
    cookies = get_amazon_cookies()
    driver.get("https://www.amazon.com.br")
    
    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})
    
    driver.get(url)
    time.sleep(3)
    
    products = []
    
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
                        'menu': menu,
                        'type': type_,
                        'filter': filter_,
                        'subfilter': subfilter_,
                    }
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
                print(f"\033[93m Amazon\033[0m - Processando página \033[93m{current_page}\033[0m de \033[92m{menu}\033[0m > \033[94m{type_}\033[0m > \033[96m{filter_}\033[0m > \033[95m{subfilter_}\033[0m")

                driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                break

    except Exception as e:
        print(f"\033[1;91mErro principal: {str(e)}\033[0m")
    finally:
        print(f"Total coletado em \033[92m{menu}\033[0m > \033[94m{type_}\033[0m > \033[96m{filter_}\033[0m: \033[93m{len(products)}\033[0m")
    
    return pd.DataFrame(products)

def scrape_kabum_category(url, menu, type_, filter_, subfilter_):
    driver.get(url)
    time.sleep(3)
    
    products = []
    
    try:
        while True:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.productCard'))
            )

            items = driver.find_elements(By.CSS_SELECTOR, 'div.productCard')
            
            for item in items:
                try:
                    global product_id_counter
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
                        'menu': menu,
                        'type': type_,
                        'filter': filter_,
                        'subfilter': subfilter_,
                    }
                    product_id_counter += 1
                    
                    try:
                        product_data['name'] = item.find_element(By.CSS_SELECTOR, 'span.nameCard').text
                    except NoSuchElementException:
                        pass

                    try:
                        price = item.find_element(By.CSS_SELECTOR, 'span.priceCard').text
                        product_data['price'] = price if price else 'Preço não disponível'
                    except NoSuchElementException:
                        pass

                    try:
                        product_data['image_url'] = item.find_element(By.CSS_SELECTOR, 'img.imageCard').get_attribute('src')
                    except NoSuchElementException:
                        pass

                    try:
                        product_link = item.find_element(By.CSS_SELECTOR, 'a.productLink').get_attribute('href')
                        product_data['product_link'] = product_link
                        product_data['affiliate_link'] = generate_awin_affiliate_link(product_link)
                    except NoSuchElementException:
                        pass

                    products.append(product_data)

                except Exception as e:
                    print(f"\033[91mErro ao coletar produto Kabum: {e}\033[0m")
                    continue

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'a.nextLink')
                if "disabled" in next_btn.get_attribute("class"):
                    break

                # Tentar obter o número da página atual (com fallback)
                try:
                    current_page = driver.find_element(By.CSS_SELECTOR, 'span.page.active').text
                except NoSuchElementException:
                    current_page = "?"  # Fallback se o seletor não existir
                
                print(f"\033[93m Kabum\033[0m - Processando página \033[93m{current_page}\033[0m de \033[92m{menu}\033[0m > \033[94m{type_}\033[0m > \033[96m{filter_}\033[0m > \033[95m{subfilter_}\033[0m")

                driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                break

    except Exception as e:
        print(f"\033[1;91mErro principal Kabum: {str(e)}\033[0m")
    finally:
        print(f"Total coletado em \033[92m{menu}\033[0m > \033[94m{type_}\033[0m > \033[96m{filter_}\033[0m: \033[93m{len(products)}\033[0m")
    
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
                "AMD gen 2-5": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiQU00Il19&sort=most_searched",
                "AMD gen 7-9": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiQU01Il19&sort=most_searched",
                "FM+": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiRk0yKyJdfQ==&sort=most_searched",
                "threadripper": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiV1JYOCIsInNUUjUiXX0=&sort=most_searched",
                "intel 1ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTYiXX0=&sort=most_searched",
                "Intel 2ª-3ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTUiXX0=&sort=most_searched",
                "Intel 4ª e 5ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTAiXX0=&sort=most_searched",
                "LGA 1157": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDE1NjciXX0=&sort=most_searched",
                "LGA 2011": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDIwMTEiXX0=&sort=most_searched",
                "LGA 4189": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDQxODkiXX0=&sort=most_searched",
                "LGA 4677": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDQ2NzciXX0=&sort=most_searched",
                "Intel 6ª-9ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDExNTEiXX0=&sort=most_searched",
                "intel 10ª e 11ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDEyMDAiXX0=&sort=most_searched",
                "Intel 12ª-14ª": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDE3MDAiXX0=&sort=most_searched",
                "Intel core 2": "https://www.kabum.com.br/hardware/processadores?page_number=1&page_size=100&facet_filters=eyJTb2NrZXQiOlsiTEdBIDE4NTEiXX0=&sort=most_searched",
            },
            "placa_mae": "https://www.kabum.com.br/hardware/placas-mae?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "gpu": "https://www.kabum.com.br/hardware/placa-de-video-vga?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "ram": "https://www.kabum.com.br/hardware/memoria-ram?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "hd": "https://www.kabum.com.br/hardware/disco-rigido-hd?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "ssd": "https://www.kabum.com.br/hardware/ssd-2-5?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "fonte": "https://www.kabum.com.br/hardware/fontes?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "air_cooler": "https://www.kabum.com.br/hardware/coolers/air-cooler?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "water_cooler": "https://www.kabum.com.br/hardware/coolers/water-cooler?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "placa_som": "https://www.kabum.com.br/hardware/placas-interfaces/placa-de-som?page_number=1&page_size=100&facet_filters=&sort=most_searched",
        },
        "desktop": {
            "desktop amd e intel": "https://www.kabum.com.br/computadores/pc/pc-gamer?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "desktop intel": "https://www.kabum.com.br/computadores/pc/computador-intel?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "desktop amd": "https://www.kabum.com.br/computadores/pc/computador-amd?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "mini pc": "https://www.kabum.com.br/computadores/pc/computador-mini-pc?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "IMAC": "https://www.kabum.com.br/computadores/pc/computador-imac?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "MAC mini": "https://www.kabum.com.br/computadores/pc/computador-mac-mini?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "all-in-one": "https://www.kabum.com.br/computadores/pc/all-in-one?page_number=1&page_size=100&facet_filters=&sort=most_searched",
        },
        "Notebook": {
            "Escritório": "https://www.kabum.com.br/computadores/notebooks/notebook-office?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Gamer": "https://www.kabum.com.br/computadores/notebooks/notebook-gamer?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "MacBook": "https://www.kabum.com.br/computadores/notebooks/macbook?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "ChromeBook": "https://www.kabum.com.br/computadores/notebooks/chromebook?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Acer": "https://www.kabum.com.br/computadores/notebooks/notebook-acer?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Asus": "https://www.kabum.com.br/computadores/notebooks/notebook-asus?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Dell": "https://www.kabum.com.br/computadores/notebooks/notebook-dell?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Lenovo": "https://www.kabum.com.br/computadores/notebooks/notebook-lenovo?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "MSI": "https://www.kabum.com.br/computadores/notebooks/notebook-msi?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Multi": "https://www.kabum.com.br/computadores/notebooks/notebook-multilaser?page_number=1&page_size=100&facet_filters=&sort=most_searched",
            "Positivo": "https://www.kabum.com.br/computadores/notebooks/notebook-positivo?page_number=1&page_size=100&facet_filters=&sort=most_searched",
        },
    }
}

def scrape_all_categories():
    all_products = []

    # Scraping Amazon
    for menu, categories in amazon_categories.items():
        for type_, filters in categories.items():
            for filter_, url in filters.items():
                if isinstance(url, dict):
                    for subfilter_, sub_url in url.items():
                        print(f"Scraping Amazon: {menu} > {type_} > {filter_} > {subfilter_}")
                        df = scrape_amazon_category(sub_url, menu, type_, filter_, subfilter_)
                        all_products.append(df)
                else:
                    print(f"Scraping Amazon: {menu} > {type_} > {filter_}")
                    df = scrape_amazon_category(url, menu, type_, filter_, '')
                    all_products.append(df)

    # Scraping Kabum
    for menu, categories in kabum_categories.items():
        for type_, filters in categories.items():
            for filter_, url in filters.items():
                if isinstance(url, dict):
                    for subfilter_, sub_url in url.items():
                        print(f"Scraping Kabum: {menu} > {type_} > {filter_} > {subfilter_}")
                        df = scrape_kabum_category(sub_url, menu, type_, filter_, subfilter_)
                        all_products.append(df)
                else:
                    print(f"Scraping Kabum: {menu} > {type_} > {filter_}")
                    df = scrape_kabum_category(url, menu, type_, filter_, '')
                    all_products.append(df)

    # Combinar todos os DataFrames
    if all_products:
        final_df = pd.concat(all_products, ignore_index=True)
        final_df.to_csv('products.csv', index=False, encoding='utf-8')
        print("Scraping concluído! Dados salvos em products.csv")
    else:
        print("Nenhum produto foi coletado.")

if __name__ == "__main__":
    try:
        scrape_all_categories()
    finally:
        driver.quit()