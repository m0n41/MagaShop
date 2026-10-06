from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    STATUS_CHOICES = (
        ("Buyer", "Покупатель"),
        ("Seller", "Продавец"),
    )
    
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    photo = models.ImageField(upload_to="profile/", blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    status_user = models.CharField(choices=STATUS_CHOICES, max_length=20, default="Buyer")
    
    def __str__(self):
        return f"Профиль: {self.username}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Профиль: {self.user.username}"