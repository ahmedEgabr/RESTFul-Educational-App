import itertools
from django_countries import countries
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from alteby.utils import render_alert


class PlanPrice(models.Model):

    class PriceCurrency(models.TextChoices):
        dollar = "dollar", ("$ Dollar")
        egp = "egp", ("E£ EGP")

    plan = models.ForeignKey("courses.CoursePlan", on_delete=models.CASCADE, related_name="prices")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0,
        validators=[MinValueValidator(0)]
        )
    currency = models.CharField(choices=PriceCurrency.choices, default=PriceCurrency.dollar, max_length=10, blank=True, null=True)
    countries = CountryField(multiple=True, blank=True, blank_label='(select country)')
    select_all_countries = models.BooleanField(default=False, help_text=render_alert(
        message="&#x26A0; When ckecked, all other prices is going to be deactivated.",
        tag="small",
        warning=True
        ))
    is_free_for_selected_countries = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text=render_alert(
        message="&#x26A0; When not ckecked, this price will not be visable to the students.",
        tag="small",
        warning=True
        ))

    # class Meta:
    #     unique_together = (
    #     ("plan", "amount", "currency"),
    #     ("plan", "currency"),
    #     )

    def __str__(self):
        return f"{self.id}"

    def clean_fields(self, **kwargs):
        if self.plan.is_free_for_all_countries:
            raise ValidationError(
                render_alert(
                    """
                    You cannot add prices. Plan is free for all countries.
                    """,
                    alert=True,
                    error=True
                )
            ) 
        
        if not self.is_active:
            can_deactivate = self.plan.prices.filter(is_active=True).exclude(id=self.id).exists()
            if not can_deactivate:
                raise ValidationError(
                render_alert(
                    """
                    Plan must has at least one active price.
                    """,
                    alert=True,
                    error=True
                )
            )
            else:
                return None
        
        if self.is_active:
            cannot_add_prices = self.plan.prices.filter(select_all_countries=True, is_active=True).exclude(id=self.id).exists()
            if cannot_add_prices:
                if self.id:
                    message = """
                    You cannot modify prices because you have a price the has (Select all Countries) checked.
                    """
                else:
                    message = """
                    You cannot add more prices because you have a price the has (Select all Countries) checked.
                    """
                raise ValidationError(
                    render_alert(
                        message,
                        alert=True,
                        error=True
                    )
            )
        
        # if self.is_applied_for_all_countries or self.is_free_for_all_countries:
        #     print(self.plan.prices.filter(is_active=True).exclude(id=self.id))
        #     if self.plan.prices.filter(is_active=True).exclude(id=self.id).exists():
        #         raise ValidationError(
        #         "You have to delete all prices of this plan or uncheck Is Active for all of them."
        #         )

        if self.is_default:
            has_default_price = self.plan.has_default_price(excluded_ids=[self.id])
            if has_default_price:
                raise ValidationError(
                {
                    "is_default": render_alert(
                        message="Plan with Default Price is already exists.",
                        tag="strong",
                        error=True
                        )
                }
                )

        if self.is_free_for_selected_countries and self.select_all_countries:
            raise ValidationError(
                render_alert(
                    """
                    You cannot check (select all countries) and (is free for selected countries) together in the price.
                    You can check (Is free for all countries) in the plan itself and will do the same.
                    """,
                    alert=True,
                    error=True
                )
            )
            
        if not (self.amount or self.currency or self.is_free_for_selected_countries):
            raise ValidationError({
                "amount": render_alert(
                    message="This field is required.",
                    tag="small",
                    error=True
                    ),
                "currency": render_alert(
                    message="This field is required.",
                    tag="small",
                    error=True
                    ),
                })
        
        if self.amount and not self.currency and not self.is_free_for_selected_countries:
            raise ValidationError({"currency": "This field is required."})

        if self.currency and not self.amount and not self.is_free_for_selected_countries:
            raise ValidationError({"amount": "This field is required."})
        
        if self.currency and self.amount and not self.countries and not self.select_all_countries:
            raise ValidationError({"countries": "This field is required."})

        if self.is_free_for_selected_countries and not self.countries:
            raise ValidationError({"countries": "This field is required."})
        
        if self.countries:
            repeated_country_selected = self.repeated_country_selected()
            if repeated_country_selected:
                raise ValidationError(
                    {
                        "countries": render_alert(
                        message=f"Country: {repeated_country_selected} is already selected in another Price.",
                        tag="strong",
                        error=True
                        )
                    }
                    )

         # if (self.is_free_for_selected_countries) and (self.amount or self.currency) or (
        # self.is_free_for_selected_countries and self.amount and self.currency):
        #     raise ValidationError(
        #         render_alert(
        #             "Plan price must be whether (Free for selected Countries) or Paid.",
        #             alert=True,
        #             error=True
        #         )
        #     )


        super(PlanPrice, self).clean_fields(**kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(PlanPrice, self).save(*args, **kwargs)

    def repeated_country_selected(self):
        if not self.countries:
            return None
        
        selected_countries = [country.code for country in self.countries]
            
        previously_selected_country = list(self.__class__.objects.filter(
            plan=self.plan
            ).exclude(
                id=self.id
                ).values_list(
                    "countries", 
                    flat=True
                    )
                )
        
        previously_selected_country = [item.split(",") for item in previously_selected_country]
        previously_selected_country = list(itertools.chain(*previously_selected_country))
        previously_selected_country = list(filter(lambda item: item is not '', previously_selected_country))
        if previously_selected_country:
            previously_selected_country = set(previously_selected_country)
            element_found = next((ele for ele in selected_countries if ele in previously_selected_country), None)
            if element_found:
                return dict(countries)[element_found]
        return None
