from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "price", "quantity")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "is_paid", "get_total_cost", "created_at")
    list_filter = ("status", "is_paid")
    actions = ("mark_shipped", "mark_delivered")
    inlines = [OrderItemInline]

    @admin.action(description="Отметить как отправленные")
    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")

    @admin.action(description="Отметить как доставленные")
    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered")
