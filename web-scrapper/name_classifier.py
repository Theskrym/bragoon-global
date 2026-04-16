import pandas as pd
import re
import os

def simplify_product_name(name):
    """Simplifica o nome do produto removendo informações desnecessárias"""
    name = str(name).lower()
    
    # Casos especiais primeiro
    if 'pentium gold' in name:
        match = re.search(r'pentium gold\s*(g\d+)', name, re.IGNORECASE)
        if match:
            return f"pentium {match.group(1)}"
        return "pentium gold"
    
    # Padrões para processadores AMD
    amd_patterns = [
        (r'ryzen\s*(\d)[-\s](\d{3,4}[a-z]*)', 'hyphen'),  # Ryzen 5-4500 → r5 4500
        (r'ryzen\s*(\d)\s*(\d{3,4}[a-z]*)', 'space'),     # Ryzen 5 4500 → r5 4500
        (r'ryzen\s+(\d)\s+(\d{4})[a-z]*\s+(\d{4})', 'repeated'),  # Ryzen 5 5600X 4500
        (r'ryzen\s+(?:threadripper\s+pro\s+)?(\d+[a-z]*\s*\d+)', 'other'),
        (r'(?:athlon|athon)\s+(?:ii\s+)?(\d+[a-z]*)', 'other'),
        (r'phenom\s+(?:ii\s+)?x\d+\s+(\d+)', 'other'),
        (r'a[6-9]\s+(\d+)', 'other'),
        (r'fx\s*(\d+)', 'other'),
        (r'opteron\s+(\d+)', 'other'),
        (r'epyc\s+(\d+)', 'other')
    ]
    
    # Padrões para processadores Intel
    intel_patterns = [
        (r'(?:core\s+)?i(\d+)[-\s](\d+)', 'hyphen'),  # i5-14400 → i5 14400
        (r'(?:core\s+)?i(\d+)\s+(\d+)', 'space'),     # i5 14400 → i5 14400
        (r'pentium\s*(gold)?\s*(g?\d+)', 'other'),
        (r'celeron\s*(g?\d+)', 'other'),
        (r'ultra\s+(\d+)', 'other'),
        (r'(?:xeon|core\s+2\s+duo)\s+[e-]?(\d+)', 'other')
    ]
    
    # Testar padrões AMD
    for pattern, pattern_type in amd_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            if 'ryzen' in name:
                if pattern_type in ['hyphen', 'space'] and len(match.groups()) >= 2:
                    series = match.group(1)
                    model = match.group(2).replace('-', '')
                    return f"r{series} {model}"
                elif pattern_type == 'repeated' and len(match.groups()) >= 3:
                    series = match.group(1)
                    model = match.group(2)  # Pega o primeiro número de modelo (5600)
                    return f"r{series} {model}"
                else:
                    series_match = re.search(r'ryzen\s*(\d)', name, re.IGNORECASE)
                    if series_match:
                        return f"r{series_match.group(1)}"
            return match.group(1) if match.groups() else ''
    
    # Testar padrões Intel
    for pattern, pattern_type in intel_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            if 'core' in name or 'i\d' in name:
                if pattern_type in ['hyphen', 'space'] and len(match.groups()) >= 2:
                    series = match.group(1)
                    model = match.group(2).replace('-', '')
                    return f"i{series} {model}"
                else:
                    return f"i{match.group(1)}" if match.groups() else ''
            elif 'pentium' in name:
                if len(match.groups()) >= 2:
                    return f"pentium {match.group(2)}" if match.group(2) else 'pentium'
                return f"pentium {match.group(1)}" if match.groups() else 'pentium'
            elif 'celeron' in name:
                return f"celeron {match.group(1)}" if match.groups() else 'celeron'
            return match.group(1) if match.groups() else ''
    
    # Padrão genérico para outros componentes
    words = re.sub(r'\(.*?\)|\[.*?\]|\d+[A-Za-z]+Hz|\d+[A-Za-z]*[Ww]att?', '', name)
    words = re.sub(r'\b(amd|intel|nvidia|geforce|rtx|gtx|radeon|series|pro|processador|,)\b', '', words, flags=re.IGNORECASE)
    words = re.split(r'\s+', words.strip())
    simplified = ' '.join([w for w in words if w and len(w) > 1][:3])
    
    return simplified if simplified else name

def clean_final_name(name):
    """Remove especificamente a palavra 'ryzen' mantendo r3/r5/r7 e limpa o resultado final"""
    if not isinstance(name, str):
        return name
    
    # Remove apenas a palavra 'ryzen' (case insensitive)
    name = re.sub(r'\bryzen\b', '', name, flags=re.IGNORECASE)
    
    # Remove frequências (GHz/MHz)
    name = re.sub(r'\b\d+[a-z]*hz\b', '', name, flags=re.IGNORECASE)
    
    # Remove espaços extras e hifens
    name = name.replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def classify_products(input_excel, output_excel, reference_csv):
    # Ler o arquivo Excel original
    df = pd.read_excel(input_excel)
    
    # Criar a coluna name_classified
    df['name_classified'] = df['name'].apply(simplify_product_name)
    
    # Aplicar a limpeza final APÓS toda a classificação
    df['name_classified'] = df['name_classified'].apply(clean_final_name)
    
    # Agora processar para adicionar atributos baseados no tipo
    reference_df = pd.read_csv(reference_csv)
    
    # Dicionário de mapeamento de tipo para colunas relevantes
    type_columns = {
        'cpu': ['modelo', 'fabricante', 'soquete'],
        'placa_mae': ['fabricante', 'soquete', 'chipset'],
        'memoria_ram': ['fabricante', 'tamanho', 'velocidade'],
        'fonte': ['fabricante', 'potencia', 'certificacao'],
    }
    
    # Processar cada linha para adicionar atributos
    for index, row in df.iterrows():
        product_type = str(row['type']).strip().lower()
        
        if product_type in type_columns:
            # Procurar no CSV de referência
            ref_match = None
            classified_name = str(row['name_classified']).lower()
            
            for ref_index, ref_row in reference_df.iterrows():
                ref_model = str(ref_row['modelo']).lower()
                if (ref_model in classified_name or 
                    classified_name in ref_model or
                    re.search(rf'\b{re.escape(ref_model)}\b', classified_name)):
                    ref_match = ref_row
                    break
            
            if ref_match is not None:
                for col in type_columns[product_type]:
                    col_name = f"{product_type}_{col}"
                    if col in ref_match and pd.notna(ref_match[col]):
                        df.at[index, col_name] = ref_match[col]
    
    # Salvar o resultado final
    df.to_excel(output_excel, index=False)
    print(f"Arquivo processado e salvo como {output_excel}")

if __name__ == "__main__":
    # Caminhos relativos ao script (funciona em qualquer computador)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(script_dir, 'output')
    
    input_excel = os.path.join(output_dir, 'produtos.xlsx')
    output_excel = os.path.join(output_dir, 'produtos_classificados.xlsx')
    reference_csv = os.path.join(output_dir, 'classificador.csv')
    
    classify_products(input_excel, output_excel, reference_csv)