from django.shortcuts import render
from django.views.generic import TemplateView

class AboutView(TemplateView):
    template_name = "pages/about.html"
    
class DeliveryView(TemplateView):
    template_name = "pages/delivery.html"
    
class ContactsView(TemplateView):
    template_name = "pages/contacts.html"