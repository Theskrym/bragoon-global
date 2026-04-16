import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import re
import os

# ==============================================
# 1. Configuração Inicial
# ==============================================

# Caminhos relativos ao script (funciona em qualquer computador)
script_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(script_dir, 'output')

# Carregar lista de processadores conhecidos
processadores_csv = os.path.join(output_dir, 'classificador.csv')
df_processadores = pd.read_csv(processadores_csv)
processadores_conhecidos = df_processadores['modelo'].str.lower().tolist()  # Usando a coluna 'modelo'

# Filtrar valores vazios (NaN) da lista de processadores
processadores_conhecidos = [proc for proc in processadores_conhecidos if pd.notna(proc)]

# Carregar dados do Excel com produtos
input_path = os.path.join(output_dir, 'produtos.xlsx')
df_produtos = pd.read_excel(input_path)

# ==============================================
# 2. Pré-processamento e Modelo de Similaridade
# ==============================================

# Função para limpar texto
def preprocess_text(text):
    if pd.isna(text):  # Se o texto for vazio (NaN), retornar string vazia
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove pontuações
    text = re.sub(r'\d+ghz|\d+mb|lga\d+|am\d+', '', text)  # Remove specs irrelevantes
    return text

# Vetorização TF-IDF
vectorizer = TfidfVectorizer(preprocessor=preprocess_text)
X = vectorizer.fit_transform(processadores_conhecidos)

# Treinar modelo
model = NearestNeighbors(n_neighbors=1, metric='cosine')
model.fit(X)

# ==============================================
# 3. Função para Identificação de Processadores
# ==============================================

def encontrar_processador(texto):
    try:
        if pd.isna(texto):  # Se o texto for vazio (NaN), retornar None
            return None
        texto_limpo = preprocess_text(texto)
        vetor = vectorizer.transform([texto_limpo])
        distancia, indice = model.kneighbors(vetor)
        
        # Definir um limiar de distância para considerar como "não encontrado"
        limiar_distancia = 0.8  # Ajuste esse valor conforme necessário
        if distancia[0][0] > limiar_distancia:
            return None  # Retorna None se a distância for muito alta
        else:
            return processadores_conhecidos[indice[0][0]].upper()
    except:
        return None  # Retorna None em caso de erro

# ==============================================
# 4. Processamento do Excel
# ==============================================

# Adicionar todas as colunas do CSV ao DataFrame de produtos
# Inicializa as colunas com valores vazios (None)
for coluna in df_processadores.columns:
    if coluna not in df_produtos.columns:  # Adicionar apenas se a coluna não existir
        df_produtos[coluna] = None  # Inicializar com valores vazios

# Processar cada linha do DataFrame de produtos
for index, row in df_produtos.iterrows():
    if row['type'] == 'CPU':
        # Buscar o modelo mais próximo no CSV
        modelo_identificado = encontrar_processador(row['name'])
        if modelo_identificado:
            # Encontrar as informações correspondentes no CSV
            processador_info = df_processadores[df_processadores['modelo'].str.lower() == modelo_identificado.lower()]
            if not processador_info.empty:
                # Preencher as colunas no DataFrame de produtos
                for coluna in df_processadores.columns:
                    df_produtos.at[index, coluna] = processador_info[coluna].values[0]
    elif row['type'] == 'placa_mae':
        # Para placas-mãe, buscar fabricante, soquete e chipset no CSV
        # Aqui você pode adicionar lógica específica para placas-mãe se necessário
        # Por enquanto, as colunas já estão inicializadas como None
        pass

# Salvar resultados
output_path = os.path.join(output_dir, 'produtos-classificados.xlsx')
df_produtos.to_excel(output_path, index=False)

print(f"Processamento concluído! Arquivo salvo em: {output_path}")