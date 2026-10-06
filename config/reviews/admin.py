from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_active", "created_at")
    list_filter = ("rating", "is_active")
    actions = ("activate", "deactivate")

    @admin.action(description="Активировать отзывы")
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Деактивировать отзывы")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
