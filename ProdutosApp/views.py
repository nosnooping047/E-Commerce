from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Produto
from collections import Counter


def produtos(request):
    if request.method == "POST":
        if 'adicionar_carrinho' in request.POST:
            produto_id = request.POST.get('produto_id')
            if produto_id:
                cart = Counter(request.session.get('cart', []))
                cart[produto_id] += 1
                request.session['cart'] = list(cart.elements())
                request.session['preco_frete'] = 0
                request.session.save()
                referer = request.META.get('HTTP_REFERER')
                page = request.GET.get('page', referer)
                return redirect(page)

        buscarproduto1 = request.POST.get('buscarproduto')
        if buscarproduto1 is not None:
            produtos = Produto.objects.filter(
                Q(nome__icontains=buscarproduto1) |
                Q(descricao__icontains=buscarproduto1) |
                Q(valor_venda__icontains=buscarproduto1)
            ).order_by('-data_lancamento')
        else:
            produtos = Produto.objects.all().order_by('-data_lancamento')
    else:
        produtos = Produto.objects.all().order_by('-data_lancamento')

    paginator = Paginator(produtos, 9)
    page = request.GET.get('page', 1)

    try:
        produtos_paginados = paginator.page(page)
    except PageNotAnInteger:
        produtos_paginados = paginator.page(1)
    except EmptyPage:
        produtos_paginados = paginator.page(paginator.num_pages)

    tem_produtos = produtos.count()

    return render(request, 'listar_produtos.html', {'produtos': produtos_paginados, 'tem_produtos': tem_produtos})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from UsuariosCadastroApp.models import PerfilUsuario  # Importe o modelo do perfil do usuário do seu aplicativo
from collections import Counter

def carrinho(request):
    if request.method == "POST":
        if 'remover_carrinho' in request.POST:
            produto_id = request.POST.get('produto_id')
            cart = Counter(request.session.get('cart', []))
            if produto_id in cart:
                cart[produto_id] -= 1
                if cart[produto_id] == 0:
                    del cart[produto_id]
            request.session['cart'] = list(cart.elements())
            request.session['preco_frete'] = 0
            request.session.save()
            return redirect('carrinho')
        elif 'adicionar_carrinho' in request.POST:
            produto_id = request.POST.get('adicionar_carrinho')
            cart = Counter(request.session.get('cart', []))
            cart[produto_id] += 1
            request.session['cart'] = list(cart.elements())
            request.session['preco_frete'] = 0
            request.session.save()
            return redirect('carrinho')
    else:
        perfil_usuario = None
        if request.user.is_authenticated:
            perfil_usuario, created = PerfilUsuario.objects.get_or_create(user=request.user)

        cart_ids = request.session.get('cart', [])
        request.session['preco_frete'] = 0
        request.session.save()

        valor_total = 0
        cart_counter = Counter(cart_ids)
        produtos_no_carrinho = [(Produto.objects.get(id=int(produto_id)), quantidade) for produto_id, quantidade in cart_counter.items()]
        valor_total = sum(produto.valor_venda * quantidade for produto, quantidade in produtos_no_carrinho)

        '''email_do_usuario = request.user.email
        print("Email: views", email_do_usuario)'''

        
        if len(produtos_no_carrinho) == 0:
            return redirect('produtos')
        else:
            '''preferencia_id = criar_preferencia(email_do_usuario, produtos_no_carrinho)'''

            return render(request, 'carrinho.html', {'produtos_no_carrinho': produtos_no_carrinho, 'valor_total': valor_total, 'perfil_usuario': perfil_usuario})


def pagamento(request):
    if request.user.is_authenticated:
        
        perfil_usuario = None
        if request.user.is_authenticated:
            perfil_usuario, created = PerfilUsuario.objects.get_or_create(user=request.user)

        cart_ids = request.session.get('cart', [])
        valor_total = 0
        cart_counter = Counter(cart_ids)
        produtos_no_carrinho = [(Produto.objects.get(id=int(produto_id)), quantidade) for produto_id, quantidade in cart_counter.items()]
        valor_total = sum(produto.valor_venda * quantidade for produto, quantidade in produtos_no_carrinho)
        
        tot = float(valor_total) + float(request.session['preco_frete'])
        print(tot)

        if len(produtos_no_carrinho) == 0:
            return redirect('produtos')
        else:
            return render(request, 'pagamento.html', {'produtos_no_carrinho': produtos_no_carrinho, 'valor_total': tot, 'perfil_usuario': perfil_usuario})
    else:
        return redirect('login')

import json
import uuid
import mercadopago
import requests
from django.http import JsonResponse, HttpResponse

# Define a chave de acesso global
ACCESS_TOKEN = "TEST-6261472583087320-030722-67cee6801b468dc3905e491f11041cf1-180251525"

def process_payment(request):
    try:
        # Cria uma instância do SDK do Mercado Pago
        sdk = mercadopago.SDK(ACCESS_TOKEN)

        # Gera um UUID único
        idempotency_key = str(uuid.uuid4())

        # Configura as opções de requisição
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': idempotency_key
        }

        # Decodifica os dados da requisição POST
        data = json.loads(request.body.decode('utf-8'))

        # Extrai os dados necessários do payload da requisição

        tot = float(request.session['preco_frete'])+float(data.get('transaction_amount'))
        print(tot)

        payment_data = {
            "transaction_amount": tot,
            "token": data.get('token'),
            "description": data.get('description'),
            "installments": int(data.get('installments')),
            "payment_method_id": data.get('payment_method_id'),
            "payer": {
                "email": data.get('payer', {}).get('email'),
                "identification": {
                    "type": data.get('payer', {}).get('identification', {}).get('type'),
                    "number": data.get('payer', {}).get('identification', {}).get('number')
                }
            }
        }
        
        # Cria o pagamento usando o SDK do Mercado Pago
        payment_response = sdk.payment().create(payment_data, request_options)
        payment = payment_response["response"]

        if payment["status"] == "approved":
            # limpar apenas o carrinho do usuário
            request.session['cart'] = []
            request.session['preco_frete'] = 0
            request.session.save()
            
        print("Resposta do pagamento:", payment)
        return JsonResponse(payment)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def statusDePagamento(request):
    try:
        id = '1321708843'
        url = 'https://api.mercadopago.com/v1/payments/' + id

        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + ACCESS_TOKEN
        }

        response = requests.get(url, headers=headers)
        resultado = response.json()

        return HttpResponse(resultado['status'])

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

 
import json
import requests
from django.http import JsonResponse

def calcular_frete_melhor_envio(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=400)

    if request.method == 'POST':
        request.session['preco_frete'] = 0
        request.session.save()
        data = json.loads(request.body)
        cep_destino = data.get('cep_destino')
        if not cep_destino:
            return JsonResponse({'error': 'CEP de destino não fornecido'}, status=400)

        # Construa os dados da solicitação para a API do Melhor Envio
        requestData = {
            "from": {
                "postal_code": "11055010"
            },
            "to": {
                "postal_code": cep_destino
            },
            "products": [
                {
                    "id": "x",
                    "width": 11,
                    "height": 17,
                    "length": 11,
                    "weight": 0.3,
                    "insurance_value": 10.1,
                    "quantity": 1
                }
            ],
            "options": {
                "receipt": False,
                "own_hand": False
            },
            "services": "1,2,18"
        }

        # Faça a solicitação para a API do Melhor Envio
        url = "https://melhorenvio.com.br/api/v2/me/shipment/calculate"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYmFmMTRmOWQ5ZTk5YzBmMmE2NDczNDFkYThiN2FmMmMwNWZkNWRmYWM4N2Y0OWYyZGZmZGY1MDBlNGYwNmQ1ZGRmNTY3MDY0NzBkYWM5MTUiLCJpYXQiOjE3MTA0NDQ5ODMuNDcwMjc1LCJuYmYiOjE3MTA0NDQ5ODMuNDcwMjc4LCJleHAiOjE3NDE5ODA5ODMuNDUwMjk5LCJzdWIiOiI5YjkwNjUzNC01ZDMyLTQ3MzItYjdkZi1jYmZlM2NjNWE4ODkiLCJzY29wZXMiOlsic2hpcHBpbmctY2FsY3VsYXRlIl19.4Ah77NSkvZ5VphM-f0yQf7-gcGFMnJTl6CrC5gukZc8kpS6kJZj6k2n2NDLDpc4ScsCgg_JvonhkUtDxeBzuSCYSXr69VSEG0taK0jY1b7qqDO45cstlsRNcu91PZCYMnYI4rbiFfRq4Wx6243wPUfVEM2QJFHpTHvsO_XDS6Rp_UBSBmJVk3-6Ma0TI8gxDDsCLvOC0NEFDUNGMD9xxrZuy4l9CBb8kF_-fHr8_iBjkGsHiNJ8mkZcTz6ce4IwnWn5Q0BNluptcviQvMfD6Kq7NUMt982Sg8K4r5a2uBKJQ-5zvWv5zaerGA3jguhBRbDorSJcb7HMKXEhB4ueFEuKndZjw9pjoU-psYF04sxzgjgT5ozzueEqSP3k-Eewl80WxcscbEU73_209Y1WueST6Z2Q82I_SS4mS6icfp26QEVHJ6k5bWxxfMYAid5q_ht1K4AyXrQvURfqzc8oR4OTwy_Iyhs3gttocxw_ENi3dW8c3FM4FimpctRECavqJXm_lMCLpV3mlqrbfQHVcaWOp67F8FZbyS6R0KFrEcSr_aSK1LXQazZOLodwo6z97AFLeIOputTA3TyzZ-8I8JsRJ51VGbW7D8FBxV9kCr-i9JlvU0z0Q-mOm1UUFSoDvdIKGoQbe6zmziWxcYPk478wH40bEmMnlEJ0ab3BBSUs",  # Substitua 'token' pela sua chave de API
            "User-Agent": "Aplicação anonytechtech@gmail.com"
        }
        response = requests.post(url, headers=headers, data=json.dumps(requestData))
        
        if response.status_code == 200:
            return JsonResponse(response.json(), status=200, safe=False)
        else:
            return JsonResponse({'error': 'Erro ao calcular frete'}, status=response.status_code)


def calcular_preco_total_produto(request):
    cart_ids = request.session.get('cart', [])
    valor_total = 0
    cart_counter = Counter(cart_ids)
    produtos_no_carrinho = [(Produto.objects.get(id=int(produto_id)), quantidade) for produto_id, quantidade in cart_counter.items()]
    valor_total = sum(produto.valor_venda * quantidade for produto, quantidade in produtos_no_carrinho)
    return valor_total

import requests
import json
from django.http import JsonResponse

def processar_selecao_frete(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=400)
    
    valor_total_produto = calcular_preco_total_produto(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        cep_destino = data.get('cep_destino')
        frete_selecionado_id = data.get('frete_selecionado')

        if not cep_destino:
            return JsonResponse({'error': 'CEP de destino não fornecido'}, status=400)
        # Verificar se o frete selecionado está vazio
        if frete_selecionado_id is None:
            return JsonResponse({'valor_frete': float(valor_total_produto)}, status=200)

        # Construa os dados da solicitação para a API do Melhor Envio
        requestData = {
            "from": {
                "postal_code": "11055010"
            },
            "to": {
                "postal_code": cep_destino
            },
            "products": [
                {
                    "id": "x",
                    "width": 11,
                    "height": 17,
                    "length": 11,
                    "weight": 0.3,
                    "insurance_value": 10.1,
                    "quantity": 1
                }
            ],
            "options": {
                "receipt": False,
                "own_hand": False
            },
            "services": "1,2,18"
        }

        # Faça a solicitação para a API do Melhor Envio
        url = "https://melhorenvio.com.br/api/v2/me/shipment/calculate"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYmFmMTRmOWQ5ZTk5YzBmMmE2NDczNDFkYThiN2FmMmMwNWZkNWRmYWM4N2Y0OWYyZGZmZGY1MDBlNGYwNmQ1ZGRmNTY3MDY0NzBkYWM5MTUiLCJpYXQiOjE3MTA0NDQ5ODMuNDcwMjc1LCJuYmYiOjE3MTA0NDQ5ODMuNDcwMjc4LCJleHAiOjE3NDE5ODA5ODMuNDUwMjk5LCJzdWIiOiI5YjkwNjUzNC01ZDMyLTQ3MzItYjdkZi1jYmZlM2NjNWE4ODkiLCJzY29wZXMiOlsic2hpcHBpbmctY2FsY3VsYXRlIl19.4Ah77NSkvZ5VphM-f0yQf7-gcGFMnJTl6CrC5gukZc8kpS6kJZj6k2n2NDLDpc4ScsCgg_JvonhkUtDxeBzuSCYSXr69VSEG0taK0jY1b7qqDO45cstlsRNcu91PZCYMnYI4rbiFfRq4Wx6243wPUfVEM2QJFHpTHvsO_XDS6Rp_UBSBmJVk3-6Ma0TI8gxDDsCLvOC0NEFDUNGMD9xxrZuy4l9CBb8kF_-fHr8_iBjkGsHiNJ8mkZcTz6ce4IwnWn5Q0BNluptcviQvMfD6Kq7NUMt982Sg8K4r5a2uBKJQ-5zvWv5zaerGA3jguhBRbDorSJcb7HMKXEhB4ueFEuKndZjw9pjoU-psYF04sxzgjgT5ozzueEqSP3k-Eewl80WxcscbEU73_209Y1WueST6Z2Q82I_SS4mS6icfp26QEVHJ6k5bWxxfMYAid5q_ht1K4AyXrQvURfqzc8oR4OTwy_Iyhs3gttocxw_ENi3dW8c3FM4FimpctRECavqJXm_lMCLpV3mlqrbfQHVcaWOp67F8FZbyS6R0KFrEcSr_aSK1LXQazZOLodwo6z97AFLeIOputTA3TyzZ-8I8JsRJ51VGbW7D8FBxV9kCr-i9JlvU0z0Q-mOm1UUFSoDvdIKGoQbe6zmziWxcYPk478wH40bEmMnlEJ0ab3BBSUs",  # Substitua 'token' pela sua chave de API
            "User-Agent": "Aplicação anonytechtech@gmail.com"
        }
        response = requests.post(url, headers=headers, data=json.dumps(requestData))

        if response.status_code == 200:
            response_data = response.json()
            for option in response_data:
                if option['id'] == frete_selecionado_id:
                    tot = float(option.get('price'))+float(valor_total_produto)

                    request.session['preco_frete'] = float(option.get('price'))
                    request.session.save()

                    return JsonResponse({'valor_frete': tot}, status=200)
                    
            return JsonResponse({'error': 'ID de frete selecionado não encontrado'}, status=400)
        else:
            return JsonResponse({'error': 'Erro ao calcular frete'}, status=response.status_code)

