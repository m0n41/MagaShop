from django.urls import path
from .views import AboutView, DeliveryView, ContactsView

app_name = 'pages'

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("delivery/", DeliveryView.as_view(), name="delivery"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
]
