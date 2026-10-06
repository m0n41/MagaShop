from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order, OrderItem
from cart.cart import Cart
from catalog.models import Product
from django.conf import settings
from django.db import transaction
from decimal import Decimal
from coupon.models import Coupon

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ["first_name", "last_name", "email", "phone", "address", "city"]
    
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial["first_name"] = user.first_name
            initial["last_name"] = user.last_name
            initial["email"] = user.email
            if hasattr(user, "profile"):
                initial["address"] = user.profile.address
                initial["phone"] = user.profile.phone
                initial["city"] = user.profile.city
        return initial
    
    @transaction.atomic
    def form_valid(self, form):
        cart = Cart(self.request)
        if len(cart) == 0:
            return redirect("cart:detail")
        form.instance.user = self.request.user

        products = []
        subtotal = Decimal("0")

        for item in cart:
            product = Product.objects.select_for_update().get(pk=item["product"].pk)
            quantity = item["quantity"]

            if product.stock < quantity:
                form.add_error(None,f'Недостаточно товара "{product.name}". 'f'Доступно: {product.stock}.')
                return self.form_invalid(form)

            products.append((product, quantity))
            subtotal += product.price * quantity

        discount = Decimal("0")
        coupon_id = self.request.session.get("coupon_id")
        print("coupon_id из session:", coupon_id)
        
        if coupon_id:
            try:
                coupon = Coupon.objects.get(pk=coupon_id)
            except Coupon.DoesNotExist:
                form.add_error(None, "Купон не найден.")
                return self.form_invalid(form)

            if not coupon.is_valid():
                form.add_error(None, "Купон недействителен или истёк.")
                return self.form_invalid(form)

            if (coupon.min_order_amount is not None and subtotal < coupon.min_order_amount):
                form.add_error(None, f"Минимальная сумма заказа для купона: " f"{coupon.min_order_amount}."
                )
                return self.form_invalid(form)

            discount = subtotal * Decimal(coupon.discount) / Decimal("100")

        form.instance.discount = discount
        response = super().form_valid(form)

        for product, quantity in products:
            OrderItem.objects.create(order=self.object,product=product,price=product.price,quantity=quantity)
            product.stock -= quantity
            product.save(update_fields=["stock"])

        cart.clear()
        self.request.session.pop("coupon_id", None)

        mail = EmailMessage(
            subject="Подтверждение заказа",
            body=f"Спасибо за ваш заказ. Номер вашего заказа: {self.object.pk}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.object.email],
        )
        mail.send()

        return response
        
    def get_success_url(self):
        return reverse("orders:detail", kwargs={"pk": self.object.pk})
    
class OrderListView(LoginRequiredMixin, ListView):
    template_name = "orders/order_list.html"
    model = Order
    context_object_name = "orders"
    paginate_by = 12
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "orders/order_detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
class OrderBuyView(OrderCreateView):
    template_name = "orders/order_form.html"
    