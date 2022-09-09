# Django
from django.core.management.base import BaseCommand

# Local Django
from courses.models import Lecture, LectureOverlap


class Command(BaseCommand):
    help = 'Migrate Lecture topics.'

    def handle(self, *args, **kwargs):
        lectures = Lecture.objects.all()
        for lecture in lectures:
            try:
                LectureOverlap.objects.get_or_create(topic=lecture.topic, lecture=lecture, order=lecture.order)
            except:
                pass
        self.stdout.write(self.style.SUCCESS("Done."))
        