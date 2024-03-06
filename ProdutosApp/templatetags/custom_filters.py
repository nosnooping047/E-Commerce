from django import template
import locale
from decimal import Decimal

register = template.Library()

def formatar_moeda(valor):
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')  # Defina a localização para o Brasil
    return locale.currency(valor, grouping=True, symbol=None)

register.filter('formatar_moeda', formatar_moeda)


@register.filter
def total_venda(produtos_no_carrinho):
    total = sum(produto.valor_venda for produto in produtos_no_carrinho)
    return total


@register.filter(name='mul')
def mul(value, arg):
    try:
        return value * arg
    except TypeError:
        return value


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)