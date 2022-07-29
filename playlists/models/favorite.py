from django.db import models


class Favorite(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="favorites")
    lecture = models.ManyToManyField("courses.Lecture", blank=True)

    def __str__(self):
          return self.user.email

    def add(self, lecture):
        self.lectures.add(lecture)
        self.save()

    def remove(self, lecture):
        self.lectures.remove(lecture)
        self.save()
