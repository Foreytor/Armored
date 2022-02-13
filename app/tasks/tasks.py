import re
import sys
import os
from finance.models import *
from celery import shared_task
import uuid


@shared_task
def taskTranslation(accountNumber, userRecipient, transactions):
    try:
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
            accounts.balance = accounts.balance - Decimal(value)
            accounts.save()
            # Кладем на счета:
            accountAccount.balance = accountAccount.balance + Decimal(value)
            accountAccount.save()

        operation.status = 'Готово'
        operation.save()
    except:
        operation.status = 'Ошибка'
        operation.save()
    return True


if __name__ == '__main__':
    pass
