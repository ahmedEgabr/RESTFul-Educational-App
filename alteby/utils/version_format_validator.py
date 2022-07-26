from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class VersionFormatValidator(validators.RegexValidator):
    regex = r"^[0-9][0-9]{0,1}([.][0-9]{1,2}[.][0-9]{1,2})?$"
    message = "Please enter a valid version format"
    flags = 0
