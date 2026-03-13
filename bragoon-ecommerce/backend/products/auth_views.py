"""
Endpoints de autenticação para o BRAGOON Store
Login, Registro e confirmação de usuário
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Endpoint de Login
    POST /api/login/
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email e senha são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Buscar usuário por email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Email ou senha incorretos'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verificar senha
        if not user.check_password(password):
            return Response(
                {'error': 'Email ou senha incorretos'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Gerar ou obter token
        token, created = Token.objects.get_or_create(user=user)

        logger.info(f'✅ Login bem-sucedido: {email}')

        return Response({
            'success': True,
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    Endpoint de Registro
    POST /api/register/
    {
        "email": "user@example.com",
        "username": "username",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username') or email  # Use email como username se não fornecido
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        # Validações
        if not email or not password:
            return Response(
                {'error': 'Email e senha são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {'error': 'Senha deve ter pelo menos 6 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar se email já existe
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Este email já está cadastrado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar se username já existe
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Este username já existe'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Criar novo usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Gerar token
            token, _ = Token.objects.get_or_create(user=user)

            logger.info(f'✅ Novo usuário registrado: {email}')

            return Response({
                'success': True,
                'message': 'Usuário cadastrado com sucesso!',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'❌ Erro ao registrar usuário: {str(e)}')
            return Response(
                {'error': f'Erro ao registrar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserViewSet(APIView):
    """
    Endpoint para obter dados do usuário autenticado
    GET /api/user/me/
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Usuário não autenticado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_authenticated': True
        })
