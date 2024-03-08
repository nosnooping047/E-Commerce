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
            return redirect('carrinho')
        elif 'adicionar_carrinho' in request.POST:
            produto_id = request.POST.get('adicionar_carrinho')
            cart = Counter(request.session.get('cart', []))
            cart[produto_id] += 1
            request.session['cart'] = list(cart.elements())
            return redirect('carrinho')
    else:
        cart_ids = request.session.get('cart', [])
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

            return render(request, 'carrinho.html', {'produtos_no_carrinho': produtos_no_carrinho, 'valor_total': valor_total})


import json
import mercadopago
from django.http import JsonResponse
import requests  # Importe a biblioteca requests

import uuid



def process_payment(request):
    access_token = "TEST-6261472583087320-030722-67cee6801b468dc3905e491f11041cf1-180251525"
    sdk = mercadopago.SDK(access_token)

    # Gere um UUID único
    idempotency_key = str(uuid.uuid4())

    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {
        'x-idempotency-key': idempotency_key
    }
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    # Extrair os dados necessários
    token = data.get('token')
    payment_method_id = data.get('payment_method_id')
    transaction_amount = data.get('transaction_amount')
    installments = data.get('installments')
    description = data.get('description')
    email = data.get('payer', {}).get('email')
    identificationType = data.get('payer', {}).get('identification', {}).get('type')
    identificationNumber = data.get('payer', {}).get('identification', {}).get('number')
    issuer_id = data.get('issuer_id')
    
    payment_data = {
        "transaction_amount": float(transaction_amount),
        "token": token,
        "description": description,
        "installments": int(installments),
        "payment_method_id": payment_method_id,
        "payer": {
            "email": email,
            "identification": {
                "type": identificationType,
                "number": identificationNumber
            }
        }
    }
    payment_response = sdk.payment().create(payment_data, request_options)
    payment = payment_response["response"]

    print("Resposta do pagamento:", payment)
    return JsonResponse(payment)

'''
def process_payment(request):
    if request.method == 'POST':
        try:
            sdk = mercadopago.SDK(access_token)
            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {
                'x-idempotency-key': '<SOME_UNIQUE_VALUE>'
            }
            # Decodificar o JSON recebido
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            # Extrair os dados necessários
            token = data.get('token')
            payment_method_id = data.get('payment_method_id')
            transaction_amount = data.get('transaction_amount')
            installments = data.get('installments')
            description = data.get('description')
            email = data.get('payer', {}).get('email')
            identificationType = data.get('payer', {}).get('identification', {}).get('type')
            identificationNumber = data.get('payer', {}).get('identification', {}).get('number')
            issuer_id = data.get('issuer_id')

            # Preparar os dados do pagamento
            payment_data = {
                "transaction_amount": float(transaction_amount),
                "token": token,
                "description": description,
                "installments": int(installments),
                "payment_method_id": payment_method_id,
                "payer": {
                    "email": email,
                    "identification": {
                        "type": identificationType,
                        "number": identificationNumber
                    }
                }
            }

            # Criar o pagamento usando o SDK do Mercado Pago
            payment_response = sdk.payment().create(payment_data)
            payment = payment_response["response"]
            print(payment)
            # Retornar uma resposta com os detalhes do pagamento
            return JsonResponse(payment)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)

    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

  
def process_payment(request):
    if request.method == 'POST':

        access_token = "TEST-6261472583087320-030722-67cee6801b468dc3905e491f11041cf1-180251525"
        data = json.loads(request.body)

        token = data.get('token')
        payment_method_id = data.get('payment_method_id')
        transaction_amount = data.get('transaction_amount')
        installments = data.get('installments')
        description = data.get('description')
        email = data.get('payer', {}).get('email')
        identificationType = data.get('identificationType')
        identificationNumber = data.get('identificationNumber')
        issuer_id = data.get('issuer_id')

        payload = {
            "transaction_amount": 100.5,
            "token": "token",
            "description": description,
            "installments": installments,
            "payment_method_id": payment_method_id,
            "issuer_id": issuer_id,
            "payer": {
                "email": email
            }
        }
        
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-idempotency-key': '<SOME_UNIQUE_VALUE>',
            'Authorization': 'Bearer ' + access_token
        }           

        
        print(payload)
        response = requests.post('https://api.mercadopago.com/v1/payments', json=payload, headers=headers)
        resultado = response.json()

        print("Result: ", resultado)
        # Aqui você pode manipular o resultado da API de pagamento.
        return JsonResponse(resultado)




def process_payment(request):
    if request.method == 'POST':
        result_request = json.loads(request.body.decode('utf-8'))
        access_token = "APP_USR-8894352011608591-080301-74476fed4ede9408193e11b38c930d03-180251525"
        # Verifica se o token de acesso está presente e não é vazio
        if not access_token:
            return JsonResponse({'error': 'Token de acesso não fornecido'})

        payload = {
            "transaction_amount": 100.5,
            "token": result_request.get('token'),
            "description": result_request.get('description'),
            "installments": result_request.get('installments'),
            "payment_method_id": result_request.get('payment_method_id'),
            "issuer_id": result_request.get('issuer_id'),
            "payer": {
                "email": result_request.get('payer').get('email')
            }
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        response = requests.post('https://api.mercadopago.com/v1/payments', json=payload, headers=headers)
        resultado = response.json()
        print("Result: ", resultado)
        return JsonResponse(resultado)

    return JsonResponse({'error': 'Método de requisição inválido'})



import json
import mercadopago
from django.http import JsonResponse

def process_payment(request):
    sdk = mercadopago.SDK("TEST-6261472583087320-030722-67cee6801b468dc3905e491f11041cf1-180251525")

    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {
        'x-idempotency-key': '<SOME_UNIQUE_VALUE>'
    }

    try:
        request_values = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Erro ao analisar o corpo da solicitação JSON'})

    payment_data = {
        "transaction_amount": float(request_values["transaction_amount"]),
        "token": request_values["token"],
        "installments": int(request_values["installments"]),
        "payment_method_id": request_values["payment_method_id"],
        "issuer_id": request_values["issuer_id"],
        "payer": {
            "email": request_values["payer"]["email"],
            "identification": {
                "type": request_values["payer"]["identification"]["type"], 
                "number": request_values["payer"]["identification"]["number"]
            }
        }
    }

    payment_response = sdk.payment().create(payment_data, request_options)
    payment = payment_response["response"]

    print("status =>", payment["status"])

   

    return JsonResponse(payment)
'''