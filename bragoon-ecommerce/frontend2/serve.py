#!/usr/bin/env python3
"""
Servidor simples para frontend2 com suporte a CORS
Executa apenas o frontend2 na porta 3000
"""

import http.server
import socketserver
import os
import functools
from pathlib import Path

PORT = 3001
DIRECTORY = str(Path(__file__).parent)

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        """Suporta requisições GET"""
        # Redirecionar raiz para index.html
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    
    # Usar functools.partial para passar directory corretamente
    handler = functools.partial(CORSRequestHandler, directory=DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Servidor Frontend2 iniciado!")
        print(f"📍 URL: http://localhost:{PORT}")
        print(f"🏪 Acesso direto: http://localhost:{PORT}")
        print(f"📁 Diretório: {DIRECTORY}")
        print(f"🔒 CORS habilitado para todas as origens")
        print(f"\n💡 Abra em outro terminal para o backend:")
        print(f"   cd bragoon-ecommerce/backend")
        print(f"   python manage.py runserver 0.0.0.0:8000")
        print(f"\n⏹️  Pressione Ctrl+C para parar\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✋ Servidor parado.")
