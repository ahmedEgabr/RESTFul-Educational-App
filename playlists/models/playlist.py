from django.db import models


class Playlist(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="Playlists")
    name = models.CharField(max_length=20, unique=True)
    lectures = models.ManyToManyField("courses.Lecture", blank=True)

    class Meta:
        unique_together = (("user", "name"),)

    def __str__(self):
          return f'{self.user.email}-{self.name}'

    def add(self, lecture):
        self.lectures.add(lecture)
        self.save()

    def remove(self, lecture):
        self.lectures.remove(lecture)
        self.save()
