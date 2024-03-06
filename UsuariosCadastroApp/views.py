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
            return redirect('/HomeApp/home/')  # Redireciona para a página inicial após o login
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
            return redirect('/HomeApp/home/')  # Redireciona para a página inicial após o login
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
    return redirect('/HomeApp/home/')