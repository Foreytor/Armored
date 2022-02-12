from .models import *
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator



@method_decorator(login_required, name='dispatch')
class UserAccountsList(ListView):
    """Класс, где пользователь может найти и выбрать счет другого пользователя, которому он хочет перевести валюту"""
    template_name = './finance/home.html'
    model = Accounts

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['accounts'] = Accounts.objects.exclude(user=self.request.user)
        return context