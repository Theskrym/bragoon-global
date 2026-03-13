# 🚀 Como Rodar o Frontend2 Corretamente

## ⚠️ IMPORTANTE: Não Use file://

O localhost da API e o file:// causam problemas de CORS e localStorage. Você DEVE servir via HTTP.

## ✅ Solução Correta (em 2 terminais)

### Terminal 1 - Backend Django (API)
```powershell
cd bragoon-ecommerce/backend
python manage.py runserver 0.0.0.0:8000
```

Você verá:
```
Starting development server at http://127.0.0.1:8000/
```

### Terminal 2 - Frontend2
```powershell
cd bragoon-ecommerce/frontend2
python serve.py
```

Você verá:
```
✅ Servidor Frontend2 iniciado!
📍 URL: http://localhost:3000
```

## 🌐 Acessar no Navegador

Abra: **http://localhost:3000**

## 🧹 Se ainda houver problemas

1. Abra: **http://localhost:3000/limpar-cache.html**
2. Clique em "Limpar Tudo e Recarregar"
3. Espere recarregar automaticamente
4. Volte para: **http://localhost:3000**

## 🔍 Verificar saúde do sistema

Abra o console (F12) e procure por:
- ✅ `🔌 API_BASE_URL: http://localhost:8000/api`
- ✅ `✅ localStorage está funcionando`
- ✅ `✨ Produtos carregados: X`

## ❌ Se continuar com erro

1. Verifique se ambos os servidores estão rodando
2. Abra http://localhost:3000/limpar-cache.html
3. Limpe tudo
4. Recarregue a página

## 💡 Alternativa: Usar porta padrão 80

Se quiser usar http://localhost/ sem porta:
```powershell
cd bragoon-ecommerce/frontend2
python serve.py  # Mude PORT = 80 no arquivo serve.py
```

Nota: Pode precisar de admin para porta 80
