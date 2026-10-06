from django import template
from ..models import Product, Category

register = template.Library()

@register.inclusion_tag("catalog/popular_products.html", takes_context=True)
def popular_products(context): 
    queryset = Product.available.order_by("-views")[:5]
    return {"products": queryset}

@register.inclusion_tag("catalog/_category_node.html", takes_context=True)
def categories_menu(context):
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    return {"categories": queryset}

@register.filter
def remove_page_param(querydict):
    qs = querydict.copy()
    qs.pop("page", None)
    return qs.urlencode()