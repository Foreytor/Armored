from django.db import models
from django.contrib.auth.models import User
from decimal import *


class Accounts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.IntegerField(verbose_name='№ счета', unique=True)
    balance = models.DecimalField(
        verbose_name='Баланс', max_digits=18, decimal_places=2, default=Decimal('0.0'))
    dateCreate = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания счета')
    dateUpdate = models.DateTimeField(
        auto_now=True, verbose_name='Дата последнего изменения счета')

    def __str__(self):
        return str(self.account)


class Operations(models.Model):
    operation = models.CharField(
        max_length=36, verbose_name='Номер операции', unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь отправителя')
    userRecipient = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь получатель', related_name='user')
    dateCreate = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания операции')
    dateUpdate = models.DateTimeField(
        auto_now=True, verbose_name='Дата последнего события')
    status = models.CharField(max_length=11, verbose_name='Статус')

    def __str__(self):
        return str(self.operation)


class Translations(models.Model):
    operation = models.ForeignKey(
        Operations, on_delete=models.CASCADE, related_name='operation+')
    accountSender = models.ForeignKey(
        Accounts, related_name='account+', on_delete=models.CASCADE)
    accountRecipient = models.ForeignKey(
        Accounts, related_name='account+', on_delete=models.CASCADE)
    sum = models.DecimalField(
        verbose_name='Сумма перевода', max_digits=18, decimal_places=2, default=Decimal('0.0'))
    dateCreate = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания транзакции')

    def __str__(self):
        return str(self.operation)
