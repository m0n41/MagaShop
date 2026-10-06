from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Product, Category
from django.db.models import F, Q, Avg, Count
from django.shortcuts import get_object_or_404
from wishlist.utils import get_wishlist_product_ids
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProductAddForm


def parse_price(value):
    try:
        return Decimal(value)
    except (TypeError, InvalidOperation):
        return None

class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = 'products'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by("-price").select_related("category").prefetch_related("tags")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Products'
        context['wishlist_product_ids'] = get_wishlist_product_ids(self.request.user)
        return context
    
class ProductDetailView(DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        Product.objects.filter(pk=self.object.pk).update(views=F('views') + 1)
        return response
    
    def get_queryset(self):
        queryset = Product.objects.all().select_related("category").prefetch_related("images", "tags")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = Product.objects.filter(pk=self.object.pk).annotate(average_rating=Avg("reviews__rating"), reviews_count=Count("reviews"),).first()
        related_products = Product.objects.filter(
            category=self.object.category, is_available=True
        ).exclude(pk=self.object.pk)[:4]
        context["related_products"] = related_products
        context["average_rating"] = stats.average_rating
        context["reviews_count"] = stats.reviews_count
        context["reviews"] = self.object.reviews.filter(is_active=True).select_related("user")
        context["wishlist_product_ids"] = get_wishlist_product_ids(self.request.user)
        return context


class SimilarProductsView(ListView):
    template_name = "catalog/similar_products.html"
    model = Product
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        self.product = get_object_or_404(Product, slug=self.kwargs.get("slug"))
        return Product.objects.filter(
            category=self.product.category, is_available=True
        ).exclude(pk=self.product.pk).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.product
        context["wishlist_product_ids"] = get_wishlist_product_ids(self.request.user)
        return context


class CategoryListView(ListView):
    template_name = "catalog/category_list.html"
    model = Product
    context_object_name = "category_product"
    paginate_by = 12

    SORT_OPTIONS = {
        "price_asc": "price",
        "price_desc": "-price",
        "popular": "-views",
        "new": "-created_at",
    }

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs.get("slug"))
        subcategories = self.category.children.filter(is_active=True)
        categories = [self.category, *subcategories]

        subcategory_slug = self.request.GET.get("subcategory")
        if subcategory_slug:
            selected = subcategories.filter(slug=subcategory_slug).first()
            if selected:
                categories = [selected]

        queryset = Product.objects.filter(category__in=categories).select_related("category")

        price_min = parse_price(self.request.GET.get("price_min"))
        price_max = parse_price(self.request.GET.get("price_max"))
        brand = self.request.GET.get("brand")
        sort = self.request.GET.get("sort")

        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)
        if brand:
            queryset = queryset.filter(brand=brand)

        return queryset.order_by(self.SORT_OPTIONS.get(sort, "name"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        subcategories = self.category.children.filter(is_active=True)
        context["subcategories"] = subcategories
        context["brands"] = (
            Product.objects.filter(category__in=[self.category, *subcategories])
            .exclude(brand="")
            .values_list("brand", flat=True)
            .distinct()
            .order_by("brand")
        )
        context["current_price_min"] = self.request.GET.get("price_min", "")
        context["current_price_max"] = self.request.GET.get("price_max", "")
        context["current_brand"] = self.request.GET.get("brand", "")
        context["current_sort"] = self.request.GET.get("sort", "")
        context["current_subcategory"] = self.request.GET.get("subcategory", "")
        context["wishlist_product_ids"] = get_wishlist_product_ids(self.request.user)
        return context
    
class SearchView(ListView):
    template_name = "catalog/search.html"
    model = Product
    context_object_name = "products"
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get("q")
        if not query:
            return Product.objects.none()
        return Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["wishlist_product_ids"] = get_wishlist_product_ids(self.request.user)
        return context
    
class ProductAddView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductAddForm
    template_name = "catalog/product_add.html"
    
    def form_valid(self, form):
        if self.request.user.status_user == "Seller":
            return super().form_valid(form)
        form.add_error(None, "Только продавцы могут добавлять товары")
        return super().form_invalid(form)