from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from .models import Review
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from catalog.models import Product
from .forms import ReviewForm

class ReviewCreteUser(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/create.html"
    
    def get_success_url(self):
        return self.object.product.get_absolute_url()
    
    def form_valid(self, form):
        product = get_object_or_404(Product, slug=self.kwargs["slug"])
        if Review.objects.filter(product=product, user=self.request.user).exists():
            form.add_error(None, "Вы уже оставляли отзыв на этот товар.")
            return self.form_invalid(form)
        form.instance.product = product
        form.instance.user = self.request.user
        messages.success(self.request, "Отзыв успешно добавлен")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, slug=self.kwargs["slug"])
        context["product"] = product
        return context
        