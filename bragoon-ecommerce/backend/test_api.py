#!/usr/bin/env python
import requests
import json
import time

# URL do backend
BASE_URL = 'http://localhost:8000/api'

print("=" * 70)
print("TESTANDO API DE AUTENTICAÇÃO DO BRAGOON STORE")
print("=" * 70)

# Aguardar um momento para garantir que o servidor está rodando
print("\n⏳ Aguardando... (certifique-se de que o Django está rodando em outro terminal)")
time.sleep(2)

# Teste 1: Registrar novo usuário
print("\n" + "=" * 70)
print("TESTE 1: REGISTRO DE NOVO USUÁRIO")
print("=" * 70)

user_data = {
    'username': f'testuser_{int(time.time())}',
    'email': f'testuser_{int(time.time())}@example.com',
    'password': 'senha123',
    'first_name': 'Test',
    'last_name': 'User'
}

print(f"\nEnviando para: {BASE_URL}/register/")
print(f"Dados: {json.dumps(user_data, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(f'{BASE_URL}/register/', json=user_data, timeout=5)
    
    print(f"\n✓ Status: {response.status_code}")
    print(f"✓ Headers: {dict(response.headers)}")
    
    try:
        resp_json = response.json()
        print(f"✓ Response:\n{json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("\n✅ REGISTRO BEM-SUCEDIDO!")
            token = resp_json.get('token')
            email = resp_json.get('user', {}).get('email')
            print(f"   Token: {token[:20]}...")
            print(f"   Email: {email}")
        elif response.status_code == 400:
            print(f"\n❌ ERRO DE VALIDAÇÃO: {resp_json.get('error', 'Erro desconhecido')}")
        else:
            print(f"\n❌ ERRO {response.status_code}")
    except:
        print(f"✓ Response (texto): {response.text[:200]}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ ERRO DE CONEXÃO: Certifique-se de que o Django está rodando!")
    print(f"   Erro: {e}")
except Exception as e:
    print(f"\n❌ ERRO: {e}")

# Teste 2: Login com usuário criado
print("\n" + "=" * 70)
print("TESTE 2: LOGIN COM USUÁRIO CRIADO")
print("=" * 70)

login_data = {
    'email': user_data['email'],
    'password': user_data['password']
}

print(f"\nEnviando para: {BASE_URL}/login/")
print(f"Dados: {json.dumps(login_data, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(f'{BASE_URL}/login/', json=login_data, timeout=5)
    
    print(f"\n✓ Status: {response.status_code}")
    
    try:
        resp_json = response.json()
        print(f"✓ Response:\n{json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("\n✅ LOGIN BEM-SUCEDIDO!")
        else:
            print(f"\n❌ ERRO {response.status_code}")
    except:
        print(f"✓ Response (texto): {response.text[:200]}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ ERRO DE CONEXÃO")
except Exception as e:
    print(f"\n❌ ERRO: {e}")

# Teste 3: Listar usuários no banco
print("\n" + "=" * 70)
print("TESTE 3: USUÁRIOS NO BANCO DE DADOS")
print("=" * 70)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print(f"\n✓ Total de usuários: {User.objects.count()}")
for user in User.objects.all():
    print(f"   - {user.username} ({user.email})")

