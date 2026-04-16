#!/usr/bin/env python
"""
Script para iniciar o Django e rodar os testes
Isso ajuda a garantir que tudo está funcionando
"""
import subprocess
import time
import sys
import os

print("=" * 70)
print("INICIADOR DE SERVIDOR + TESTES")
print("=" * 70)

# Caminho do backend
backend_path = r"c:\Users\enzo.machado\OneDrive - CESMAC\TRABALHO 2 COUR\bragoon-global-master\bragoon-ecommerce\backend"

print(f"\n📁 Diretório: {backend_path}")

# Iniciar servidor Django em background
print("\n🚀 Iniciando o servidor Django na porta 8000...")
print("   (O servidor rodará em background)")

try:
    # Iniciar o servidor em background
    proc = subprocess.Popen(
        ['python', 'manage.py', 'runserver'],
        cwd=backend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("   ✓ Processo iniciado com PID:", proc.pid)
    
    # Aguardar o servidor iniciar
    print("\n⏳ Aguardando servidor iniciar...")
    time.sleep(5)
    
    # Verificar se o processo ainda está rodando
    if proc.poll() is None:
        print("   ✓ Servidor está rodando")
    else:
        print("   ✗ Servidor falhou ao iniciar")
        stdout, stderr = proc.communicate()
        print(f"\nStdout:\n{stdout}")
        print(f"\nStderr:\n{stderr}")
        sys.exit(1)
    
    # Agora rodar os testes
    print("\n🧪 Rodando testes da API...")
    test_proc = subprocess.run(
        ['python', 'test_api.py'],
        cwd=backend_path,
        capture_output=False,
        text=True
    )
    
    # Aguardar um momento antes de terminar
    time.sleep(1)
    
finally:
    # Encerrar o servidor Django
    print("\n🛑 Encerrando servidor Django...")
    try:
        proc.terminate()
        proc.wait(timeout=5)
        print("   ✓ Servidor encerrado")
    except:
        proc.kill()
        print("   ✓ Servidor forçadamente encerrado")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
