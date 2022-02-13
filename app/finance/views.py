from pdb import post_mortem
from .models import *
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q
import uuid

from .forms import TranslationForm, SearchForm
from django.contrib.auth.models import User


@method_decorator(login_required, name='dispatch')
class UserAccountsList(ListView):
    """Класс, где пользователь может найти и выбрать счет другого пользователя, которому он хочет перевести валюту"""
    template_name = './finance/home.html'
    model = Accounts

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['accounts'] = Accounts.objects.exclude(
            user=self.request.user).order_by('user')
        return context


@method_decorator(login_required, name='dispatch')
class TranslationDetals(DetailView):
    """Класс, где пользователь может найти и выбрать счет другого пользователя, которому он хочет перевести валюту"""
    template_name = './finance/translation_detal.html'
    model = Accounts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Счета пользователя отправителя
        context['accountsUser'] = Accounts.objects.filter(
            user=self.request.user).order_by('user')

        # Имя пользователя отправителя
        context['user'] = context['accountsUser'][0].user

        # Счет получателя
        context['accountNumber'] = kwargs['object']

        form = TranslationForm(user_id=context['accountsUser'][0].user)

        context['form'] = form

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        # id пользователя отправителя
        request.session['userRecipient'] = context['user'].pk
        # id счета получателя
        request.session['accountNumber'] = context['accountNumber'].pk
        try:
            context['error'] = request.session['error']
            request.session.pop('error')
        except KeyError as e:
            pass

        return self.render_to_response(context)


@method_decorator(login_required, name='dispatch')
class StartTranslation(View):
    """Класс, инициализирующий перевод"""

    def post(self, request, *args, **kwargs):
        userRecipient = request.session['userRecipient']
        #userSend = request.session['userSend']
        # id счета получателя
        accountNumber = request.session['accountNumber']
        form = TranslationForm(userRecipient, request.POST)

        if form.is_valid():
            # С каких счетов списывать
            selectAccount = form.cleaned_data['selectAccount']
            # Сколько списывать
            sumTranslatio = Decimal(form.cleaned_data['sumTranslatio'])
            # Общая сумма счетов с которых надо списать
            sumAll = Decimal(0)
            for i in selectAccount:
                sumAll = sumAll + i.balance
            # Праверка на наличие суммы
            if sumAll < sumTranslatio:
                request.session['error'] = 'Недостаточно средст для перевода'
                return HttpResponseRedirect(f'/{accountNumber}')
            # Сколько списать с каждого
            kol = sumTranslatio / len(selectAccount)
            transactions = dict()
            for i in selectAccount:
                transactions[i.account] = kol

            temp = Decimal(0)
            i = 1
            sKey = 0
            for key, value in transactions.items():
                temp = + value
                i += 1
                if i == len(transactions):
                    sKey = key

            if temp != sumTranslatio:
                for key, value in transactions.items():
                    if sKey == key:
                        transactions[key] = transactions[key].quantize(
                            Decimal("1.00"), ROUND_CEILING)
                    else:
                        transactions[key] = transactions[key].quantize(
                            Decimal("1.00"), ROUND_HALF_EVEN)

            # Распределение если сумма есть, но по разным счетам
            for key, value in transactions.items():
                account = Accounts.objects.get(account=key)
                if value > account.balance:
                    request.session['error'] = 'Не удалось распределить сумму автоматический'
                    return HttpResponseRedirect(f'/{accountNumber}')
            # Создание обекта операции
            operation = Operations()
            operation.operation = uuid.uuid4()
            accountAccount = Accounts.objects.get(pk=accountNumber)
            operation.user = accountAccount.user
            operation.userRecipient = User.objects.get(pk=int(userRecipient))
            operation.status = 'В обработке'
            operation.save()

            for key, value in transactions.items():
                translation = Translations()
                translation.operation = operation
                accounts = Accounts.objects.get(account=key)
                translation.accountSender = accounts
                translation.accountRecipient = Accounts.objects.get(
                    pk=accountNumber)
                translation.sum = value
                translation.save()

                # Списываем со счета:
                accounts.balance = accounts.balance - value
                accounts.save()

                # Кладем на счета:
                accountAccount.balance = accountAccount.balance + value
                accountAccount.save()

            # Списывание с каждого счета и запись информации об этом

            print(transactions)
        return HttpResponseRedirect('/')


@method_decorator(login_required, name='dispatch')
class TranslationListUser(ListView):
    """Класс, для просмотра своих переводов"""

    template_name = './finance/translation_list_user.html'
    model = Translations

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Accounts.objects.exclude(
            user=self.request.user).order_by('user')
        account = Accounts.objects.filter(user=self.request.user)
        translation = Translations.objects.filter(Q(accountSender__in=account)|Q(accountRecipient__in=account))
        paginator = Paginator(translation, 4)
        context['translations'] = paginator.page(
            self.request.GET.get('page', 1))
        
        context['search'] = SearchForm()

        return context

@method_decorator(login_required, name='dispatch')
class SearchList(ListView):
    """Класс, для просмотра срезультатов поиска"""

    template_name = './finance/search_results.html'
    model = Translations

    def get_queryset(self): # новый
        search = self.request.GET.get('search')

        operation = Operations.objects.filter(operation__icontains=search)
        object_list = Translations.objects.filter(operation__in=operation)
        return object_list

    #def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)        
    #     context['search'] = SearchForm()

    #     return context

    # def post(self, request, *args, **kwargs):
    #     form = SearchForm(request.POST)
    #     if form.is_valid():
    #         search = form.cleaned_data['search']
    #         operation = Operations.objects.filter(operation__icontains=search)
    #         self.context['searchList'] = Translations.objects.filter(operation__in=operation)
    #         return HttpResponseRedirect('/searchlist/')