from django.db import models


class WatchHistory(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="watch_history")
    lectures = models.ManyToManyField("courses.Lecture", blank=True)

    class Meta:
        verbose_name_plural = 'Watch history'

    def __str__(self):
          return f'{self.user.email}-Watch History'

    def add(self, lecture):
        self.lectures.add(lecture)
        self.save()
