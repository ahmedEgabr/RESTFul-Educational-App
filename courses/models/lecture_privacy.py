from django.db import models
from courses.models.abstract_privacy import Privacy

class LecturePrivacy(Privacy):

    lecture = models.OneToOneField("courses.Lecture", on_delete=models.CASCADE, blank=True, related_name="privacy")

    is_downloadable = models.BooleanField(default=True, verbose_name="Is Downloadable")
    is_downloadable_for_enrolled_users_only = models.BooleanField(
        default=True,
        verbose_name="Is Downloadable for Enrolled Users Only"
    )

    is_quiz_available = models.BooleanField(default=True, verbose_name="Is Quiz Available")
    is_quiz_available_for_enrolled_users_only = models.BooleanField(
        default=True,
        verbose_name="Is Quiz Available for Enrolled Users Only"
    )

    def __str__(self):
          return self.lecture.title
