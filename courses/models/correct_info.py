from django.db import models

class CorrectInfo(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE)
    min_from = models.CharField(blank=True, max_length=100)
    min_to = models.CharField(blank=True, max_length=100)
    scientific_evidence = models.TextField(blank=True)

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.lecture.title}'
