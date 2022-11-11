from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Feedback(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="feedbacks")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.IntegerField(
    validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_rating",
                check=models.Q(rating__range=(1, 5)),
            ),
        ]

    def __str__(self):
          return f'{self.user.email}-{self.course.title}'
