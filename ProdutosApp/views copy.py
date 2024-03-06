from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Produto
from collections import Counter
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse

def produtos(request):
    if request.method == "POST":
        # Verifica se o formulário é para adicionar ou remover um item do carrinho
        if 'adicionar_carrinho' in request.POST:
            produto_id = request.POST.get('produto_id')
            if produto_id:
                cart = Counter(request.session.get('cart', []))
                cart[produto_id] += 1
                request.session['cart'] = list(cart.elements())
                # Obtém o número da página atual do paginator
                referer = request.META.get('HTTP_REFERER')
                page = request.GET.get('page', referer)
                return redirect(page)
            
        # Se uma pesquisa está sendo realizada
        buscarproduto1 = request.POST.get('buscarproduto')
        if buscarproduto1 is not None:  # Verifica se buscarproduto1 é None
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
        print('remover carrinho')
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
            print('adicionar carrinho')
            produto_id = request.POST.get('adicionar_carrinho')
            cart = Counter(request.session.get('cart', []))
            cart[produto_id] += 1
            request.session['cart'] = list(cart.elements())
            return redirect('carrinho')
    else:
        cart_ids = request.session.get('cart', [])
        valor_total = 0  # Inicializa o valor total como zero
        cart_counter = Counter(cart_ids)
        produtos_no_carrinho = [(Produto.objects.get(id=int(produto_id)), quantidade) for produto_id, quantidade in cart_counter.items()]

        # Calcula o valor total do carrinho
        valor_total = sum(produto.valor_venda * quantidade for produto, quantidade in produtos_no_carrinho)
        print(len(produtos_no_carrinho))

        if len(produtos_no_carrinho) == 0:
            print('Carrinho vazio')
            return redirect('produtos')
        else:
            return render(request, 'carrinho.html', {'produtos_no_carrinho': produtos_no_carrinho, 'valor_total': valor_total})
        
import mercadopago
def checkout(request):
    if request.method == 'POST':
        # Processar dados do formulário de checkout
        '''full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')'''
        
        # Recuperar IDs e quantidades do carrinho da sessão
        cart_ids = request.session.get('cart', [])
        cart_counter = Counter(cart_ids)
        
        # Lista de itens para a preferência do Mercado Pago
        items = []
        total_amount = 0  # Inicializa o valor total como 0

        for produto_id, quantidade in cart_counter.items():
            produto = Produto.objects.get(id=produto_id)
            item_price = float(produto.valor_venda)
            total_amount += item_price * quantidade  # Adiciona ao valor total
            item = {
                "title": produto.nome,
                "quantity": quantidade,
                "currency_id": "BRL",
                "unit_price": item_price
            }
            items.append(item)

        # Use o ID do usuário autenticado como ID_DO_PAGADOR
        id_do_pagador = request.user.id

        # Crie um pagamento com o Mercado Pago
        sdk = mercadopago.SDK("TEST-5623534421492977-021311-36f84a69d748fe8392e4fab79428ea50-180251525")
        payment_data = {
            "transaction_amount": total_amount,  # Define o valor total corretamente
            "token": '<TOKEN_DO_CARTÃO>',  # Substitua pelo token do cartão
            "installments": 1,
            "payer": {
                "type": "customer",
                "id": id_do_pagador  # Use o ID_DO_PAGADOR como ID do usuário autenticado
            }
        }
        
        payment_response = sdk.payment().create(payment_data)

        # Verifique se o pagamento foi criado com sucesso
        if payment_response["status"] == 201:
            # Obtenha o link de pagamento
            payment_link = payment_response["response"]["init_point"]
            # Redirecione para o link de pagamento
            return redirect(payment_link)
        else:
            # Se houver algum erro ao criar o pagamento, exiba uma mensagem de erro
            return HttpResponse("Erro ao criar o pagamento.")
    else:
        return render(request, 'checkout.html')


