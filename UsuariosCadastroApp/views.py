from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
from django.db import models

def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Ops! Parece que a senha e a confirmação de senha não coincidem.')
            return redirect('/UsuariosCadastroApp/cadastro')
        
        username = request.POST.get('username')
        email = request.POST.get('email')     
        user_ = User.objects.filter(username=username)
        email_ = User.objects.filter(email=email)

        if user_.exists() or email_.exists():
            messages.add_message(request, constants.ERROR, 'Desculpe, parece que o nome de usuário ou o endereço de e-mail já estão em uso.')
            return redirect('/UsuariosCadastroApp/cadastro')
        try:
            # Crie o usuário e faça login imediatamente
            user = User.objects.create_user(username=username, password=senha, email=email)
            auth.login(request, user)  # Faz login automaticamente após o cadastro
            messages.add_message(request, constants.SUCCESS, 'Parabéns! Seu cadastro foi concluído com sucesso. Bem-vindo à nossa comunidade!')
            return redirect('/ProdutosApp/produtos/')  # Redireciona para a página inicial após o login
        except:
            messages.add_message(request, constants.ERROR, 'Ops! Encontramos um problema no servidor ao processar sua solicitação.')
            redirect('/UsuariosCadastroApp/cadastro')
            
def logar(request):
    if request.method == "GET":
        print(request.user)
        return render(request, 'login.html')
    elif request.method == "POST":
        print(request.user)
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        # Autenticar o usuário pelo nome de usuário e senha
        user = auth.authenticate(request, username=username, password=senha)
        
        if user is not None: 
            auth.login(request, user)
            print("logado como ", user.email)
            messages.add_message(request, constants.SUCCESS, 'Login bem-sucedido!')
            return redirect('/ProdutosApp/produtos/')  # Redireciona para a página inicial após o login
        else:
            messages.add_message(request, constants.ERROR, 'Ops! Nome de usuário ou senha incorretos.')
            return redirect('/UsuariosCadastroApp/logar')




from django.contrib import auth

def logout(request):
    # Salva a sessão do carrinho antes de limpar as informações de autenticação do usuário
    cart_session = request.session.get('cart', [])
    
    # Limpa apenas as informações de autenticação do usuário
    auth.logout(request)  
    
    # Restaura a sessão do carrinho após o logout
    request.session['cart'] = cart_session
    
    # Redireciona para a página de login
    return redirect('/ProdutosApp/produtos/')


import requests
from django.http import JsonResponse

def buscar_endereco(request):
    if request.method == 'GET' and request.GET.get('ajax') == 'true': # Verifica se o parâmetro 'ajax' está presente e é 'true'
        cep = request.GET.get('cep')
        response = requests.get(f'https://api.postmon.com.br/v1/cep/{cep}')
        data = response.json()
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Requisição inválida'})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario
from cpf_field.validators import validate_cpf
from django.core.exceptions import ValidationError

@login_required
def minha_conta(request):
    perfil_usuario, created = PerfilUsuario.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Atualize os dados do perfil do usuário apenas se os campos estiverem preenchidos no formulário
        perfil_usuario.nome = request.POST.get('nome', perfil_usuario.nome)
        perfil_usuario.ultimo_nome = request.POST.get('ultimo_nome', perfil_usuario.ultimo_nome)
        perfil_usuario.telefone = request.POST.get('telefone', perfil_usuario.telefone)
        perfil_usuario.cep = request.POST.get('cep', perfil_usuario.cep)
        perfil_usuario.rua = request.POST.get('rua', perfil_usuario.rua)
        perfil_usuario.numero = request.POST.get('numero', perfil_usuario.numero)
        perfil_usuario.bairro = request.POST.get('bairro', perfil_usuario.bairro)
        perfil_usuario.cidade = request.POST.get('cidade', perfil_usuario.cidade)
        perfil_usuario.estado = request.POST.get('estado', perfil_usuario.estado)

        # Validar o CPF antes de salvar
        cpf = request.POST.get('cpf',perfil_usuario.cpf)
        if cpf:
            try:
                validate_cpf(cpf)  # Isso levantará uma exceção se o CPF for inválido
                perfil_usuario.cpf = cpf
            except ValidationError:
                # Handle a exceção de CPF inválido aqui
                # Por exemplo, exibir uma mensagem de erro para o usuário
                messages.add_message(request, constants.ERROR, 'CPF inválido. Por favor, tente novamente.')
                pass

        # Salvar o objeto do perfil do usuário
        perfil_usuario.save()
        
        return redirect('minha_conta')
    else:
        # Se a requisição não for POST, renderize o template com os dados do perfil do usuário
        return render(request, 'minha_conta.html', {'perfil_usuario': perfil_usuario})

def minhas_compras(request):
    return render(request, 'minhas_compras.html')
