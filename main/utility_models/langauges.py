from django.db import models 


class Languages(models.TextChoices):
        arabic = "arabic", ("Arabic")
        english = "english", ("English")
        ar_and_en = "arabic_english", ("Arabic/English")
        