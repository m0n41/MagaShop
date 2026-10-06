from django.contrib import admin
from .models import Category, Product, ProductImage
from django.utils.html import format_html
from django.db.models import Count

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "products_count")
    list_filter = ("is_active", "parent")
    prepopulated_fields = {"slug": ("name",)}
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))

    @admin.display(description="Товаров", ordering="products_count")
    def products_count(self, obj):
        return obj.products_count


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("photo_preview", "name", "category", "price", "old_price", "stock", "is_available", "views")
    list_filter = ("is_available", "category")
    list_editable = ("price", "stock", "is_available")
    actions = ("make_available", "make_unavailable")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    
    @admin.action(description="Сделать доступными")
    def make_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description="Сделать недоступными")
    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px;">', obj.image.url)
        return "—"
