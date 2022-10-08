from django.db import models


class LectureQuality(models.Model):

    class Qualities(models.IntegerChoices):
        _2160 = 2160, ("2160p")
        _1440 = 1440, ("1440p")
        _1080 = 1080, ("1080p")
        _720 = 720, ("720p")
        _480 = 480, ("480p")
        _360 = 360, ("360p")
        _240 = 240, ("240p")
        _144 = 144, ("144p")

    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE, related_name="qualities")
    video = models.FileField()
    quality = models.CharField(choices=Qualities.choices, max_length=20)

    class Meta:
        verbose_name_plural = 'Lecture Qualities'
        ordering = ('-quality',)

    def __str__(self):
        return f'{self.lecture}-{self.quality}'

    def get_quality_display(self):
        quality = getattr(self.Qualities, f'_{self.quality}')
        return quality.label

print(LectureQuality.Qualities.choices)
