import os
import re
import time
import gc
import random
import certifi
import urllib3
import requests
import pandas as pd
import threading
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from queue import Queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
script_dir = os.path.dirname(os.path.realpath(__file__))

# Tentar importar webdriver-manager (opcional)
try:
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    HAS_WEBDRIVER_MANAGER = False

# Tentar importar Firefox service
try:
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    HAS_FIREFOX = True
except ImportError:
    HAS_FIREFOX = False

# Configuração de session HTTP com connection pooling
http_session = requests.Session()
http_adapter = requests.adapters.HTTPAdapter(
    pool_connections=20,
    pool_maxsize=20,
    max_retries=3
)
http_session.mount('http://', http_adapter)
http_session.mount('https://', http_adapter)

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


product_id_counter = 0
product_id_lock = None

class DriverPool:
    """Pool de drivers Chrome reutilizáveis para múltiplas threads"""
    def __init__(self, pool_size=4):
        self.pool_size = pool_size
        self.available_drivers = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_drivers()
    
    def _initialize_drivers(self):
        """Inicializa drivers no pool"""
        print(f"🔧 Criando pool de {self.pool_size} drivers Chrome...")
        for i in range(self.pool_size):
            driver = create_chrome_driver()
            if driver:
                self.available_drivers.put(driver)
                print(f"   ✓ Driver {i+1}/{self.pool_size} criado")
            else:
                print(f"   ✗ Falha ao criar driver {i+1}")
    
    def get_driver(self, timeout=30):
        """Obtém driver do pool (espera se necessário)"""
        return self.available_drivers.get(timeout=timeout)
    
    def return_driver(self, driver):
        """Devolve driver para o pool"""
        self.available_drivers.put(driver)
    
    def close_all(self):
        """Fecha todos os drivers do pool"""
        while not self.available_drivers.empty():
            try:
                driver = self.available_drivers.get_nowait()
                driver.quit()
            except:
                pass

driver_pool = None  # Variável global

def find_chrome_executable():
    """Procura Chrome/Chromium instalado no sistema"""
    possible_paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Chromium\Application\chrome.exe',
        os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def find_firefox_executable():
    """Procura Firefox instalado no sistema"""
    possible_paths = [
        r'C:\Program Files\Mozilla Firefox\firefox.exe',
        r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
        os.path.expandvars(r'%ProgramFiles%\Mozilla Firefox\firefox.exe'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def create_chrome_driver():
    """Criar driver Chrome - com fallbacks"""
    chrome_executable = find_chrome_executable()
    
    if not chrome_executable:
        print("⚠️  Chrome não encontrado no sistema")
        return None
    
    try:
        chrome_options = ChromeOptions()
        chrome_options.binary_location = chrome_executable
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Tentar com webdriver-manager primeiro
        if HAS_WEBDRIVER_MANAGER:
            try:
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
               
                return driver
            except Exception:
                pass
        
        # Fallback: Chrome sem webdriver-manager
        try:
            driver = webdriver.Chrome(options=chrome_options)
           
            return driver
        except Exception as e:
            print(f"⚠️  Erro ao criar Chrome driver: {e}")
            return None
            
    except Exception as e:
        print(f"⚠️  Erro ao configurar Chrome: {e}")
        return None

def create_firefox_driver():
    """Criar driver Firefox - fallback"""
    firefox_executable = find_firefox_executable()
    
    if not firefox_executable:
        return None
    
    try:
        firefox_options = FirefoxOptions()
        firefox_options.binary_location = firefox_executable
        firefox_options.add_argument("--headless")
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        
        service = FirefoxService()
        driver = webdriver.Firefox(service=service, options=firefox_options)
      
        return driver
    except Exception as e:
        print(f"⚠️  Erro ao criar Firefox driver: {e}")
        return None

def create_driver():
    """Cria driver - tenta Chrome primeiro, depois Firefox"""
    print("🔍 Procurando navegador disponível...")
    
    # Tentar Chrome
    driver = create_chrome_driver()
    if driver:
        print("✅ Chrome encontrado e iniciado")
        return driver
    
    # Fallback Firefox
    if HAS_FIREFOX:
        print("🔄 Trying Firefox como fallback...")
        driver = create_firefox_driver()
        if driver:
            print("✅ Firefox encontrado e iniciado")
            return driver
    
    print("❌ Nenhum navegador disponível!")
    return None

def format_filter_path(filter_path):
    """Formata o caminho de filtros"""
    colors = ['\033[92m', '\033[94m', '\033[96m', '\033[95m', '\033[93m', '\033[91m', '\033[36m']
    formatted_parts = []
    for i, item in enumerate(filter_path):
        color = colors[i % len(colors)]
        formatted_parts.append(f"{color}{item}\033[0m")
    return " > ".join(formatted_parts)

def create_dynamic_filter_dict(filter_path):
    """Cria dicionário dinâmico com filtros"""
    column_names = ['menu', 'type_', 'filter_', 'subfilter_']
    for i in range(4, len(filter_path)):
        column_names.append(f'subfilter_{i}')
    
    filter_dict = {}
    for i, value in enumerate(filter_path):
        filter_dict[column_names[i]] = value
    return filter_dict

def scrape_kabum_category_fast(url, filter_path):
    """Scrapa Kabum rapidamente - usando pool de drivers"""
    global driver_pool
    
    # Obtém driver do pool (espera se necessário)
    driver = None
    try:
        driver = driver_pool.get_driver(timeout=120)
    except:
        print(f"❌ Timeout ao obter driver do pool para {' > '.join(filter_path)}")
        return pd.DataFrame()
    
    products = []
    page_count = 0
    
    try:
        path_str = format_filter_path(filter_path)
        
        while True:
            page_count += 1
            print(f"\033[93m Kabum\033[0m - Página \033[93m{page_count}\033[0m de {path_str}")
            
            try:
                # Carregar página com timeout reduzido
                driver.get(url)
                
                # Esperar apenas imagens (elemento mais rápido de aparecer)
                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_all_elements_located((By.XPATH, '//img[contains(@src, "kabum.com.br/produtos")]'))
                    )
                except:
                    pass
                
                # Pequeno delay para layout renderizar
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Erro ao carregar página: {e}")
                break
            
            # Encontrar produtos
            items = []
            try:
                img_elements = driver.find_elements(By.XPATH, '//img[contains(@src, "kabum.com.br/produtos")]')
                
                if img_elements:
                    seen_containers = set()
                    for img in img_elements:
                        try:
                            container = img.find_element(By.XPATH, "ancestor::div[5]")
                            container_id = id(container)
                            if container_id not in seen_containers:
                                items.append(container)
                                seen_containers.add(container_id)
                        except:
                            pass
                
                if not items:
                    items = driver.find_elements(By.XPATH, '//div[contains(@class, "group") and contains(@class, "flex") and .//img[contains(@src, "kabum.com.br/produtos")]]')
                
            except Exception as e:
                print(f"Erro ao buscar produtos: {e}")
            
            if not items:
                break
            
            print(f"\033[92m✓ {len(items)} itens encontrados\033[0m")
            
            # Extração rápida de dados
            for item in items:
                try:
                    global product_id_counter
                    product_id_counter += 1
                    
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
                    
                    # Nome
                    try:
                        name = item.find_element(By.CSS_SELECTOR, 'span.text-ellipsis.line-clamp-2.break-normal').text.strip()
                        if name:
                            product_data['name'] = name
                    except:
                        try:
                            name = item.find_element(By.CSS_SELECTOR, 'span.text-ellipsis').text.strip()
                            if name:
                                product_data['name'] = name
                        except:
                            pass
                    
                    # Preço
                    try:
                        price_spans = item.find_elements(By.XPATH, './/span[@class="text-base font-semibold text-gray-800"]')
                        if len(price_spans) >= 2:
                            currency = price_spans[-2].text.strip()
                            value = price_spans[-1].text.strip()
                            if value and currency:
                                product_data['price'] = f"{currency} {value}"
                    except:
                        pass
                    
                    # Avaliação
                    try:
                        rating_elem = item.find_element(By.XPATH, './/span[@class="text-xs text-gray-400 font-semibold"]')
                        rating_text = rating_elem.text.strip()
                        rating_match = re.search(r'(\d+[\.,]\d+|\d+)', rating_text)
                        if rating_match:
                            product_data['rating'] = rating_match.group(1).replace(',', '.')
                    except:
                        pass
                    
                    # Imagem
                    try:
                        img = item.find_element(By.CSS_SELECTOR, 'img[width="162"]')
                        src = img.get_attribute('src')
                        if src and src.startswith('http'):
                            product_data['image_url'] = src
                    except:
                        pass
                    
                    # Link
                    try:
                        all_links = item.find_elements(By.XPATH, './/a[@href]')
                        for link in all_links:
                            href = link.get_attribute('href')
                            if href and 'kabum.com.br/hardware/' in href and '?' not in href:
                                product_data['product_link'] = href
                                product_data['affiliate_link'] = href
                                break
                        
                        if product_data['product_link'] == '#':
                            for link in all_links:
                                href = link.get_attribute('href')
                                if href and 'kabum.com.br' in href and href != '#':
                                    product_data['product_link'] = href
                                    product_data['affiliate_link'] = href
                                    break
                    except:
                        pass
                    
                    products.append(product_data)
                    
                except Exception as e:
                    continue
            
            # Próxima página
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'a.nextLink')
                aria_disabled = next_btn.get_attribute('aria-disabled')
                
                if aria_disabled == 'true' or not next_btn.is_displayed():
                    break
                
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(0.3)  # Delay mínimo
                
            except:
                break
        
        path_str = format_filter_path(filter_path)
        print(f"✓ Total em {path_str}: \033[93m{len(products)}\033[0m")
        
        return pd.DataFrame(products)
        
    finally:
        # Devolve driver para o pool ao invés de fechar
        if driver:
            driver_pool.return_driver(driver)
        gc.collect()

def scrape_categories_parallel(categories_dict, max_workers=20):
    """Scrapa múltiplas categorias em paralelo com pool de drivers"""
    global driver_pool
    
    # Inicializar pool de drivers (1 driver por 2 workers, máximo 12)
    pool_size = min(12, max(4, max_workers // 2))
    driver_pool = DriverPool(pool_size=pool_size)
    
    all_dataframes = []
    
    def process_category(key, url, filter_path):
        try:
            return scrape_kabum_category_fast(url, filter_path)
        except Exception as e:
            print(f"Erro ao processar {' > '.join(filter_path)}: {e}")
            return pd.DataFrame()
    
    def walk_categories(cat_dict, path=[]):
        tasks = []
        for key, value in cat_dict.items():
            new_path = path + [key]
            
            if isinstance(value, dict):
                # Se é dicionário, descer recursivamente
                tasks.extend(walk_categories(value, new_path))
            else:
                # Se é string (URL), é uma tarefa
                tasks.append((key, value, new_path))
        return tasks
    
    print("🚀 Iniciando scraping em paralelo...")
    print(f"   Pool de drivers: {pool_size} (reutilizáveis)")
    print(f"   Workers: {max_workers}\n")
    
    tasks = walk_categories(categories_dict)
    print(f"   Total de categorias: {len(tasks)}\n")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for key, url, path in tasks:
            future = executor.submit(process_category, key, url, path)
            futures[future] = (key, path)
        
        for future in as_completed(futures):
            key, path = futures[future]
            try:
                df = future.result()
                if len(df) > 0:
                    all_dataframes.append(df)
                    gc.collect()
            except Exception as e:
                print(f"Erro: {e}")
    
    # Fechar pool de drivers
    if driver_pool:
        driver_pool.close_all()
        print("\n✓ Pool de drivers fechado")
    
    return all_dataframes

kabum_categories= {
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

def standardize_dataframes(df_list):
    """Padroniza todos os DataFrames"""
    if not df_list:
        return df_list
    
    order = ['product_ID', 'name', 'price', 'rating', 'review_count', 'store', 
             'image_url', 'product_link', 'affiliate_link', 'menu', 'type_', 
             'filter_', 'subfilter_']
    
    all_columns = []
    for col in order:
        for df in df_list:
            if col in df.columns and col not in all_columns:
                all_columns.append(col)
    
    for df in df_list:
        for col in df.columns:
            if col.startswith('subfilter_') and col not in all_columns:
                all_columns.append(col)
    
    standardized_list = []
    for df in df_list:
        df_copy = df.copy()
        for col in all_columns:
            if col not in df_copy.columns:
                df_copy[col] = ''
        df_copy = df_copy[all_columns]
        standardized_list.append(df_copy)
    
    return standardized_list

if __name__ == "__main__":
    print("\n" + "="*90)
    print("🧪 SCRAPER OTIMIZADO - VERSÃO PARALELA COM POOL DE DRIVERS")
    print("="*90 + "\n")
    
    # Reset do contador
    product_id_counter = 0
    
    start_time = time.time()
    
    # Scrape com paralelização (20 workers)
    all_products = scrape_categories_parallel(kabum_categories, max_workers=20)
    
    elapsed_time = time.time() - start_time
    
    if all_products:
        all_products = standardize_dataframes(all_products)
        final_df = pd.concat(all_products, ignore_index=True)
        
        output_dir = os.path.join(script_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        csv_path = os.path.join(output_dir, 'produtos_otimizado.csv')
        final_df.to_csv(csv_path, index=False, encoding='utf-8')
        
        print("\n" + "="*90)
        print("📊 RESULTADOS")
        print("="*90)
        print(f"✓ Total de produtos: {len(final_df)}")
        print(f"✓ Tempo total: {elapsed_time:.2f} segundos ({elapsed_time/60:.2f} minutos)")
        print(f"✓ Velocidade: {len(final_df) / (elapsed_time/60):.0f} produtos/minuto")
        print(f"✓ Arquivo salvo: {csv_path}\n")
        
        # Estatísticas
        print("📈 ESTATÍSTICAS:")
        print(f"   Nomes: {(final_df['name'] != 'Produto sem nome').sum()}/{len(final_df)}")
        print(f"   Preços: {(final_df['price'] != 'Preço não disponível').sum()}/{len(final_df)}")
        print(f"   Links: {(final_df['product_link'] != '#').sum()}/{len(final_df)}")
        print(f"   Imagens: {(final_df['image_url'] != 'Imagem não disponível').sum()}/{len(final_df)}\n")
        
    else:
        print("❌ Nenhum produto foi coletado")
    
    print("="*90 + "\n")
