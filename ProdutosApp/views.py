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



def pagamento(request):
    if request.user.is_authenticated:
        cart_ids = request.session.get('cart', [])
        valor_total = 0
        cart_counter = Counter(cart_ids)
        produtos_no_carrinho = [(Produto.objects.get(id=int(produto_id)), quantidade) for produto_id, quantidade in cart_counter.items()]
        valor_total = sum(produto.valor_venda * quantidade for produto, quantidade in produtos_no_carrinho)

        if len(produtos_no_carrinho) == 0:
            return redirect('produtos')
        else:
            return render(request, 'pagamento.html', {'produtos_no_carrinho': produtos_no_carrinho, 'valor_total': valor_total})
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
        payment_data = {
            "transaction_amount": float(data.get('transaction_amount')),
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
            return redirect('produtos')
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
