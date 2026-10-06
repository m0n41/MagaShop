from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from catalog.models import Product
from .models import Wishlist

class WishlistView(LoginRequiredMixin, ListView):
    template_name = "wishlist/wishlist_all.html"
    context_object_name = 'wishes'
    model = Wishlist

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wish = Wishlist.objects.filter(user=request.user, product=product).first()
    if wish:
        wish.delete()
    else:
        Wishlist.objects.create(user=request.user, product=product)

    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect(product.get_absolute_url())