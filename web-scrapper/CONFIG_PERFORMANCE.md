# Configurações do Scraper Otimizado

## 🎯 Parâmetros Principais

### Paralelização
**MAX_WORKERS** = 4
- Número de threads simultâneas
- Recomendado: 4-8 (depende de CPU disponível)
- Máximo seguro: 10 (para não sobrecarregar a rede)

### Timeouts (segundos)
**PAGE_LOAD_TIMEOUT** = 20
- Tempo máximo para carregar página
- Reduzir para 15 se rede for lenta
- Aumentar para 30 em conexões muito lentas

**SCRIPT_TIMEOUT** = 10
- Tempo máximo para executar JS
- Quando desabilitado, usar 5

### Delays (segundos)
**DELAY_ENTRE_CLIQUES** = 0.3
- Delay mínimo entre ações do Selenium
- Reduzir para 0.2 em rede rápida

**DELAY_ENTRE_PAGINAS** = 0.5
- Delay ao mudar de página
- Reduzir para 0.3 para acelerar ainda mais

### Otimizações Chrome
```
--disable-images       # Desabilita carregamento de imagens
--disable-gpu          # Desabilita GPU (não necessário)
--no-sandbox           # Remove sandbox (mais rápido)
--disable-plugins      # Remove extensões
--disable-extensions   # Remove add-ons
```

Desabilitar imagens reduz tempo em ~30% mas mantém as URLs!

### Memória
**GARBAGE_COLLECT_INTERVAL** = 1 (após cada categoria)
- Força limpeza de memória
- Importante para manter <6GB

## 📊 Presets de Velocidade

### RÁPIDO (Recomendado para dados continuados)
```python
MAX_WORKERS = 4
PAGE_LOAD_TIMEOUT = 15
DELAY_ENTRE_CLIQUES = 0.2
DELAY_ENTRE_PAGINAS = 0.3
```
**Tempo estimado: 8-10 minutos**

### EQUILIBRADO (Padrão)
```python
MAX_WORKERS = 4
PAGE_LOAD_TIMEOUT = 20
DELAY_ENTRE_CLIQUES = 0.3
DELAY_ENTRE_PAGINAS = 0.5
```
**Tempo estimado: 10-15 minutos**

### CONFIÁVEL (Melhor taxa de sucesso)
```python
MAX_WORKERS = 2
PAGE_LOAD_TIMEOUT = 30
DELAY_ENTRE_CLIQUES = 0.5
DELAY_ENTRE_PAGINAS = 1.0
```
**Tempo estimado: 20-30 minutos**

### ULTRA-RÁPIDO (Apenas com rede muito boa)
```python
MAX_WORKERS = 8
PAGE_LOAD_TIMEOUT = 10
DELAY_ENTRE_CLIQUES = 0.1
DELAY_ENTRE_PAGINAS = 0.2
```
**Tempo estimado: 5-8 minutos**
**Risco: Possível perda de dados**

## 🔍 Monitoramento de Memória

### Windows
```bash
# Abrir em terminal separado para monitorar
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value
```

### Linux
```bash
watch -n 1 'free -h'
```

### Mac
```bash
top -l 1 | grep "PhysMem"
```

## ⚙️ Ajustes Recomendados

### Se usar >5GB de RAM
- Reduzir MAX_WORKERS para 2-3
- Aumentar GARBAGE_COLLECT_INTERVAL
- Processar em lotes: 1000 produtos por vez

### Se tiver CPU baixa (<4 cores)
- MAX_WORKERS = 2
- Aumentar timeouts
- Usar DELAY maior

### Se tiver conexão instável
- PAGE_LOAD_TIMEOUT = 40
- MAX_WORKERS = 1-2
- Aumentar DELAY_ENTRE_PAGINAS para 1.0

## 📝 Checklist de Performance

- [ ] Dimensionamento de workers apropriado (4-8)
- [ ] Imagens desabilitas (economiza 30% tempo)
- [ ] Garbage collection ativo
- [ ] Connection pooling habilitado
- [ ] Timeouts realistas para sua conexão
- [ ] Monitorar RAM durante execução
- [ ] Executar em período fora de pico

