#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Listar usuários existentes
print("=" * 60)
print("USUÁRIOS EXISTENTES NO BANCO")
print("=" * 60)
for user in User.objects.all():
    print(f"  ID: {user.id} | Username: {user.username} | Email: {user.email}")

print("\n" + "=" * 60)
print("TESTANDO CRIAÇÃO DE NOVO USUÁRIO")
print("=" * 60)

try:
    # Criar um novo usuário
    user = User.objects.create_user(
        username='novouser',
        email='novo@example.com',
        password='senha123',
        first_name='Novo',
        last_name='User'
    )
    print(f"✅ Usuário criado com sucesso!")
    print(f"   ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   First Name: {user.first_name}")
    print(f"   Last Name: {user.last_name}")
except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")

print("\n" + "=" * 60)
print("USUÁRIOS APÓS CRIAÇÃO")
print("=" * 60)
for user in User.objects.all():
    print(f"  ID: {user.id} | Username: {user.username} | Email: {user.email}")
