from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.translation import gettext as _

from index.forms import SendEmailForm
from .models import Subscriber, Contacted


class PhoneNumberFilter(SimpleListFilter):
    title = _("номером телефону")
    parameter_name = 'phone_number'

    def lookups(self, request, model_admin):
        return (
            ("with", _("Є")),
            ("without", _("Немає"))
        )

    def queryset(self, request, queryset):
        if self.value() == 'with':
            return queryset.exclude(phone_number__exact="")
        if self.value() == "without":
            return queryset.filter(phone_number__exact="")


class ContactedFilter(SimpleListFilter):
    title = _("контактом")
    parameter_name = 'contacted'

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Є")),
            ("no", _("Немає")),
            ("unknown", _("Ще не контактували"))
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(contacted__contacted__exact=True)
        elif self.value() == "no":
            return queryset.filter(contacted__contacted__exact=False)
        elif self.value() == "unknown":
            return queryset.filter(contacted__isnull=True)


class EmailFilter(SimpleListFilter):
    title = _("email")
    parameter_name = 'email'

    def lookups(self, request, model_admin):
        return (
            ("with", _("Є")),
            ("without", _("Немає"))
        )

    def queryset(self, request, queryset):
        if self.value() == 'with':
            return queryset.exclude(email__exact="")
        if self.value() == "without":
            return queryset.filter(email__exact="")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_filter = (PhoneNumberFilter, EmailFilter, ContactedFilter)
    search_fields = ["name", "email"]
    list_display = [field.name for field in Subscriber._meta.get_fields()]
    actions = ['mark_as_accepted', 'mark_as_refused', 'send_email']

    def mark_as_accepted(self, request, queryset):
        self.mark(request, queryset, True)

    def mark_as_refused(self, request, queryset):
        self.mark(request, queryset, False)

    def send_email(self, request, queryset):
        form = SendEmailForm(initial={'subscribers': queryset.all()})
        return render(request, 'index/email.html', {'form': form})

    mark_as_accepted.short_description = _("Помітити як сконтактовані")
    mark_as_refused.short_description = _("Помітити як несконтактовані")
    send_email.short_description = _("Надіслати email")

    def mark(self, request, queryset, accepted):
        subscribers = queryset.all()
        quantity = 0
        for subscriber in subscribers:
            quantity += 1
            try:
                subscriber.contacted.contacted = accepted
                subscriber.contacted.save()
            except ObjectDoesNotExist:
                contacted = Contacted(subscriber=subscriber, contacted=accepted)
                contacted.save()
        if accepted:
            message_bit = _("%s було помічено як сконтактовані" % quantity)
        else:
            message_bit = _("%s було помічено як несконтактовані" % quantity)
        self.message_user(request, message_bit)
