from django.db import models
from django.utils.translation import gettext as _


class Subscriber(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Ім'я")
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email")
    )
    phone_number = models.CharField(
        blank=True,
        max_length=15,
        verbose_name=_("Номер телефону")
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = _("Підписник")
        verbose_name_plural = _("Підписники")


class Contacted(models.Model):
    subscriber = models.OneToOneField(
        Subscriber,
        on_delete=models.CASCADE,
        verbose_name=_("Підписник"),
    )
    contacted = models.BooleanField()

    def __str__(self):
        return str(self.contacted)
