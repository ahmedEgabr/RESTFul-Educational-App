from django.db import models
from main.utility_models import UserActionModel, TimeStampedModel
from alteby.utils import render_alert
from django.core.exceptions import ValidationError

class LectureOverlap(UserActionModel, TimeStampedModel):
    topic = models.ForeignKey("courses.Topic", on_delete=models.CASCADE, related_name="assigned_lectures")
    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE, related_name="assigned_topics")
    order = models.IntegerField()
    
    class Meta:
        unique_together = ["topic", "lecture"]
        indexes = [
            models.Index(fields=['topic']),
            models.Index(fields=['lecture']),
        ]
    
    def __str__(self) -> str:
        return f"{self.topic.title}-{self.lecture.title}"
    
    def clean_fields(self, **kwargs):
        if self.__class__.objects.filter(topic=self.topic, order=self.order).exclude(id=self.id).exists():
            raise ValidationError(
                {
                    "order": render_alert(
                        f"""
                        Lecture with the same order in topic: {self.topic.title} is already exists.
                        """,
                        tag="strong",
                        error=True  
                        )
                }
            ) 
        super(LectureOverlap, self).clean_fields(**kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(LectureOverlap, self).save(*args, **kwargs)
    