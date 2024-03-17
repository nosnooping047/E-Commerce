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
            return redirect('cadastro')
        
        username = request.POST.get('username')
        email = request.POST.get('email')     
        user_ = User.objects.filter(username=username)
        email_ = User.objects.filter(email=email)

        if user_.exists() or email_.exists():
            messages.add_message(request, constants.ERROR, 'Desculpe, parece que o nome de usuário ou o endereço de e-mail já estão em uso.')
            return redirect('cadastro')
        try:
            # Crie o usuário e faça login imediatamente
            user = User.objects.create_user(username=username, password=senha, email=email)
            auth.login(request, user)  # Faz login automaticamente após o cadastro
            messages.add_message(request, constants.SUCCESS, 'Parabéns! Seu cadastro foi concluído com sucesso. Bem-vindo à nossa comunidade!')
            return redirect('/ProdutosApp/produtos/')  # Redireciona para a página inicial após o login
        except:
            messages.add_message(request, constants.ERROR, 'Ops! Encontramos um problema no servidor ao processar sua solicitação.')
            redirect('cadastro')
            
def logar(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = auth.authenticate(request, username=username, password=senha)
        

        if user is not None: 
            auth.login(request, user)
            print("logado como ", user.email)
            messages.add_message(request, constants.SUCCESS, 'Login bem-sucedido!')

            previous_page = request.META.get('HTTP_REFERER', '/')
            if 'carrinho' in previous_page:
                return redirect('carrinho')
            else:            
                return redirect('minha_conta')  # Redireciona para a página inicial após o login
        else:
            print("Login inválido")
            messages.add_message(request, constants.ERROR, 'Ops! Nome de usuário ou senha incorretos.')
            return redirect('login')




from django.contrib import auth

def logout(request):
    # Salva a sessão do carrinho antes de limpar as informações de autenticação do usuário
    cart_session = request.session.get('cart', [])
    
    # Limpa apenas as informações de autenticação do usuário
    auth.logout(request)  
    
    # Restaura a sessão do carrinho após o logout
    request.session['cart'] = cart_session
    previous_page = request.META.get('HTTP_REFERER', '/')
    # Redireciona para a página de login
    return redirect(previous_page)


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

import requests
from collections import Counter
from ProdutosApp.models import Produto, Compra
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta  # Importe timedelta da biblioteca datetime


def impressao_de_etiquetas(request, order_id):
    intervalo = timedelta(minutes=1)
    agora = datetime.now()

    if 'ultima_solicitacao' in request.session:
        ultima_solicitacao_str = request.session['ultima_solicitacao']
        ultima_solicitacao = datetime.fromisoformat(ultima_solicitacao_str)  # Convertendo de volta para datetime
        diferenca = agora - ultima_solicitacao

        if diferenca < intervalo:
            print("NAO IMPRIMIR. Intervalo de requisição muito curto: ", diferenca)
            return False

    request.session['ultima_solicitacao'] = agora.isoformat()  # Convertendo para string antes de armazenar na sessão
    return True

    url = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/tracking"

    payload = { "orders": [order_id] }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NTYiLCJqdGkiOiJhMmY4NjQxY2Y3NzkxYmY0ZWI5ZGU3ODQyZDUxZWYxMmZjMTBjYzVkYzI2OTA1N2Y1ZmMxYzE1Y2UzYTlkYjNlM2IwNDcwMjE2MmMzM2YyMyIsImlhdCI6MTcxMDg3OTM1MS42MDkzMjcsIm5iZiI6MTcxMDg3OTM1MS42MDkzMzEsImV4cCI6MTc0MjQxNTM1MS41OTYzNDMsInN1YiI6IjliOTljYzIyLWZlZDItNDM3My04ZTRhLTNjZDBmNmQxZmNjMiIsInNjb3BlcyI6WyJjYXJ0LXJlYWQiLCJjYXJ0LXdyaXRlIiwiY29tcGFuaWVzLXJlYWQiLCJjb21wYW5pZXMtd3JpdGUiLCJjb3Vwb25zLXJlYWQiLCJjb3Vwb25zLXdyaXRlIiwibm90aWZpY2F0aW9ucy1yZWFkIiwib3JkZXJzLXJlYWQiLCJwcm9kdWN0cy1yZWFkIiwicHJvZHVjdHMtZGVzdHJveSIsInByb2R1Y3RzLXdyaXRlIiwicHVyY2hhc2VzLXJlYWQiLCJzaGlwcGluZy1jYWxjdWxhdGUiLCJzaGlwcGluZy1jYW5jZWwiLCJzaGlwcGluZy1jaGVja291dCIsInNoaXBwaW5nLWNvbXBhbmllcyIsInNoaXBwaW5nLWdlbmVyYXRlIiwic2hpcHBpbmctcHJldmlldyIsInNoaXBwaW5nLXByaW50Iiwic2hpcHBpbmctc2hhcmUiLCJzaGlwcGluZy10cmFja2luZyIsImVjb21tZXJjZS1zaGlwcGluZyIsInRyYW5zYWN0aW9ucy1yZWFkIiwidXNlcnMtcmVhZCIsInVzZXJzLXdyaXRlIiwid2ViaG9va3MtcmVhZCIsIndlYmhvb2tzLXdyaXRlIiwid2ViaG9va3MtZGVsZXRlIiwidGRlYWxlci13ZWJob29rIl19.B5yhjNTw8k-hggMbe4VMgjOQSezsq78ymA3Z9gRQM0euPHtUFrpTotSogrj7BV1944VDFob7kUYwA2F3GsNu3xuwAdqtMfDhZ9hOF3Lg3xQwewt0qA3OfwEl6-3_fcdPWT4duE8B7EpGAfnJSwftOd7puDVKAqNXzIBscpNJNaU_Ia-lqko1RJrjg4RO2zOovrWeTyvgsDznBZQcVNSgfmV-9hVli_P1XW6HbrvrBUvJSHBKoeb3nV3xnPsmMPJRx9AAt5IYeW1v3RSsC7PduwKnszVci3PmuqkuvXT8cIhCh-8S49vScLxsSUIh_9IVN9yd8-bZNnCenUCE7vPqCGYNoyvThY5p2_vj6LwY7vxO3VdQ4s81VnjX_SPGlKjbVrqzL8k63kmrBMz5MVudbRntQKqbF0PohLbwO8jfcc3EzmU3KVRJZtqi30r31-pR0tbM86JSxNd5kbvJVufQNIi4Bmx9kSacWweOswvAGLaImKw2AnpAzYPi-tc5QV8HbdELoY6iuTv6TUMe6zrU9YFGWizNt-JBPafIpyujEd9-nBr3uZzjRuXoNmxP0bEbeTFKmGHMMVgp78uF33QtgWSgeuPSskIuLkWEWXQSBq7BF_vkvcCvxl_NKKTnP5S52xGuU8d73hDUoRNVwmNHLE9xZMb5Z_NYJ2N6WUw68Wo",  # Substitua 'token' pela sua chave de API
        "User-Agent": "Aplicação anonytechtech@gmail.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    data = response_json[next(iter(response_json))]  # Acessa o primeiro item do JSON
    tracking = data.get('tracking')
    status = data.get('status')
    id_rastreio = data.get('id')
    #print("Código de rastreamento:", tracking)

    # Atualiza os dados de Compra
    try:
        compra = Compra.objects.get(id_para_rastreio=order_id)
        compra.status = status
        compra.codigo_rastreio = tracking
        compra.save()
    except Compra.DoesNotExist:
        print("Compra não encontrada para o ID de rastreio:", order_id)
 
    #print(response.text)

from ProdutosApp.models import Compra
def minhas_compras(request):
    # Recupera as compras do usuário atual
    compras_do_usuario = Compra.objects.filter(usuario=request.user).order_by('-data_compra')

    for compra in compras_do_usuario:
        impressao_de_etiquetas(request, compra.id_para_rastreio)

    # Renderiza o template com as compras no contexto
    return render(request, 'minhas_compras.html', {'compras': compras_do_usuario})
