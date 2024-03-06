from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Produto
from collections import Counter
import mercadopago

def criar_preferencia(email_do_usuario, produtos_no_carrinho):
    sdk = mercadopago.SDK("TEST-5623534421492977-021311-36f84a69d748fe8392e4fab79428ea50-180251525")

    preference_data = {
        "items": [
            {
                "title": "My Item",
                "quantity": 1,
                "unit_price": 75.76
            }
        ]
    }
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]


    return preference["id"]

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

        email_do_usuario = request.user.email
        print("Email: views", email_do_usuario)

        
        if len(produtos_no_carrinho) == 0:
            return redirect('produtos')
        else:
            preferencia_id = criar_preferencia(email_do_usuario, produtos_no_carrinho)

            return render(request, 'carrinho.html', {'preferencia_id': preferencia_id, 'produtos_no_carrinho': produtos_no_carrinho, 'valor_total': valor_total})


from django.http import JsonResponse
import mercadopago

def process_payment(request):
    if request.method == 'POST':
        print(request.POST)
        """try:
            # Certifique-se de que todos os campos necessários estão presentes no request.POST
            transaction_amount = float(request.POST.get("transaction_amount"))
            token = request.POST.get("token")
            description = request.POST.get("description")
            installments = int(request.POST.get("installments"))
            payment_method_id = request.POST.get("payment_method_id")
            cardholder_email = request.POST.get("cardholderEmail")
            identification_type = request.POST.get("identificationType")
            identification_number = request.POST.get("identificationNumber")
            cardholder_name = request.POST.get("cardholderName")

            # Inicialize o SDK do Mercado Pago
            sdk = mercadopago.SDK("TEST-5623534421492977-021311-36f84a69d748fe8392e4fab79428ea50-180251525")

            # Dados do pagamento
            payment_data = {
                "transaction_amount": transaction_amount,
                "token": token,
                "description": description,
                "installments": installments,
                "payment_method_id": payment_method_id,
                "payer": {
                    "email": cardholder_email,
                    "identification": {
                        "type": identification_type,
                        "number": identification_number,
                    },
                    "first_name": cardholder_name,
                }
            }

            # Criação do pagamento
            payment_response = sdk.payment().create(payment_data)
            payment = payment_response["response"]

            return JsonResponse({"success": True, "payment": payment})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Método de requisição inválido"})"""
