from django import forms
from .models import Product

class ProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "brand", "description", "price", "old_price", "stock", "tags", "image"]
        labels = {
            "name": "Имя",
            "category": "Категория",
            "brand": "Бренд",
            "description": "Описание",
            "price": "Цена",
            "old_price": "Старая цена",
            "stock": "Stock",
            "tags": "Теги",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "old_price": forms.NumberInput(attrs={"class": "form-control"}),
        }