from django.db import models
from courses.models.abstract_privacy import Privacy

class LecturePrivacy(Privacy):

    lecture = models.OneToOneField("courses.Lecture", on_delete=models.CASCADE, blank=True, related_name="privacy")

    download_status = models.IntegerField(
        choices=Privacy.AvailabilityStatus.choices, 
        default=Privacy.AvailabilityStatus.AVAILABLE_FOR_ENROLLED
    )
    quiz_status = models.IntegerField(
        choices=Privacy.AvailabilityStatus.choices, 
        default=Privacy.AvailabilityStatus.AVAILABLE_FOR_ENROLLED
    )


    def __str__(self):
          return self.lecture.title
