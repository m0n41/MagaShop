from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from catalog.models import Product
from .forms import CartAddForm
from decimal import Decimal

def cart_add(request, product_id):
    if request.method == "POST":
        form = CartAddForm(request.POST)
        if form.is_valid():
            product = get_object_or_404(Product, id=product_id)
            cart = Cart(request)
            cart.add(product, form.cleaned_data['quantity'])
            messages.success(request, "Товар добавлен в корзину")
            return redirect(product.get_absolute_url())
        else:
            return render(request, 'cart/add.html', {'form': form})
    else:
        form = CartAddForm()
        return render(request, 'cart/add.html', {'form': form})

@login_required
def buy_now(request, product_id):
    # GET, не POST: если гость не залогинен, login_required уводит его на страницу
    # входа с ?next=..., а после входа Django возвращает его на этот же URL —
    # POST-данные так вернуть было бы нельзя, а GET-параметры сохраняются сами.
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get("quantity", 1))
    cart = Cart(request)
    cart.add(product, quantity)
    return redirect("orders:buy")

@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    if request.POST.get("action") == "all":
        cart.remove(product)
    else:
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1
        cart.remove(product, quantity=quantity)
    return redirect("cart:detail")

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart:detail")

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_id")
        from coupon.models import Coupon
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                cart = Cart(request)
                subtotal = sum(Decimal(item["price"]) * item["quantity"] for item in cart.cart.values())
                if coupon.min_order_amount is not None and subtotal < coupon.min_order_amount:
                    messages.error(request, f"Сумма заказа должна быть не меньше {coupon.min_order_amount} для применения этого купона.")
                else:
                    request.session["coupon_id"] = coupon.id
                    messages.success(request, "Купон успешно применен.")
            else:
                messages.error(request, "Купон недействителен или истек.")
        except Coupon.DoesNotExist:
            messages.error(request, "Купон не найден.")
    return redirect("cart:detail")

def remove_coupon(request):
    if "coupon_id" in request.session:
        del request.session["coupon_id"]
        messages.success(request, "Купон успешно удален.")
    return redirect("cart:detail")