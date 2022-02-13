from random import choice
from django import forms
from .models import *




class TranslationForm(forms.Form):
    selectAccount = forms.ModelMultipleChoiceField(queryset=Accounts.objects.all(), label='Выберите счета с которых нужно сделать перевод')
    sumTranslatio = forms.DecimalField(label='Сумма перевода')

    def __init__(self, user_id, *args, **kwargs):
        #author_id = kwargs.pop("author_id", None)
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['selectAccount'].queryset = Accounts.objects.filter(user=user_id)