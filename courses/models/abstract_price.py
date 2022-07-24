from django.db import models

class Price(models.Model):

    class PriceCurrency(models.TextChoices):
        dollar = "dollar", ("$ Dollar")
        egp = "egp", ("E£ EGP")

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(choices=PriceCurrency.choices, default=PriceCurrency.dollar, max_length=10)

    class Meta:
        abstract = True

    def __str__(self):
        return f"course-{self.course.title}:price-{self.amount}"
