import os
from django.db import models
from django.core.exceptions import ValidationError
from .time_stamp import TimeStampedModel
from alteby.utils import VersionFormatValidator


class AppVersion(TimeStampedModel):
    """ AppVersion model """
    version_format_validator = VersionFormatValidator()

    version_name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        help_text="App Version Format",
        validators=[version_format_validator],
        error_messages={
            "unique": "This app version name is already exists"
        },
        max_length=100,
        verbose_name="Version Name"
    )
    version_code = models.IntegerField(
        null=False, blank=True, unique=True, db_index=True, verbose_name="Version Code"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    is_minimum_version = models.BooleanField(default=False, verbose_name="Is Minimum Version")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "App Version"
        verbose_name_plural = "App Versions"

    def __str__(self):
        return "{0}: {1}".format(self.id, self.version_name)

    def clean(self):
        if self.version_name:
            version_code = self.get_version_code_from_version_name
            is_version_code_exists = AppVersion.objects.filter(version_code=version_code).exclude(id=self.id).exists()
            if is_version_code_exists:
                raise ValidationError({"version_code": "Version name already exist"})
            self.version_code = version_code

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def convert_version_name_to_code(version_name_str):
        """ Convert str version_name to int version_code """
        if not isinstance(version_name_str, str):
            return 0

        version_name_str_split_list = version_name_str.split(".")
        version_code_str = "".join("0{}".format(num) if (len(num) == 1) else num for num in version_name_str_split_list)
        if not version_code_str.isnumeric():
            return 0

        version_code_int = int(version_code_str)
        return version_code_int

    @property
    def get_version_code_from_version_name(self):
        """ Get version_code from int instance.version_name"""
        version_name_str = self.version_name
        version_code = self.convert_version_name_to_code(version_name_str)
        return version_code

    @classmethod
    def is_force_upgrade(cls, version_code):
        """ Get is_force_upgrade based on api int version_code """
        if not isinstance(version_code, int):
            return None

        if not version_code:
            return None

        minimum_app_version_query = cls.objects.filter(is_minimum_version=True, is_active=True)
        if not minimum_app_version_query.exists():
            return False

        latest_minimum_app_version = minimum_app_version_query.order_by("version_code").last()
        return version_code < latest_minimum_app_version.version_code

    @classmethod
    def is_recommend_upgrade(cls, version_code):
        """ retrieves is_recommend_upgrade based on api int version_code """
        if not isinstance(version_code, int):
            return None

        if not version_code:
            return None

        minimum_app_version_query = cls.objects.filter(is_minimum_version=True, is_active=True)
        if not minimum_app_version_query.exists():
            return False

        active_app_version_query = cls.objects.filter(is_active=True)
        if not active_app_version_query.exists():
            return False

        latest_minimum_app_version = minimum_app_version_query.order_by("version_code").last()
        latest_maximum_app_version = active_app_version_query.order_by("version_code").last()
        return latest_minimum_app_version.version_code <= version_code < latest_maximum_app_version.version_code
