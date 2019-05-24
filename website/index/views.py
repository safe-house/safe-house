from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from .forms import SendEmailForm
from .models import Subscriber


class IndexView(CreateView):
    template_name = "index/index.html"
    model = Subscriber
    success_url = "/"
    fields = '__all__'


class SendEmailView(FormView):
    template_name = "index/email.html"
    form_class = SendEmailForm
    success_url = reverse_lazy('admin:index_subscriber_changelist')

    def form_valid(self, form):
        subscribers = [subscriber.email for subscriber in form.cleaned_data['subscribers']]
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        email = EmailMessage(
            subject=subject,
            body=message,
            bcc=subscribers
        )
        email.send()
        user_message = '{0} subscribers emailed successfully!'.format(form.cleaned_data['subscribers'].count())
        messages.success(self.request, user_message)
        return super(SendEmailView, self).form_valid(form)
