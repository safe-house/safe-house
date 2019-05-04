from django import forms
from django.utils.translation import gettext as _

from .models import Subscriber


class SendEmailForm(forms.Form):
    subject = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Тема')}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('Повідомлення')}))
    subscribers = forms.ModelMultipleChoiceField(label="To",
                                                 queryset=Subscriber.objects.all(),
                                                 widget=forms.SelectMultiple())
