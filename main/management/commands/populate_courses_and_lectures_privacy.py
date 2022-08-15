# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Local Django
from courses.models import Course, Lecture


class Command(BaseCommand):
    help = 'Populate Courses/Lectures Privacy settings'

    def handle(self, *args, **kwargs):
        courses = Course.objects.filter(privacy=None)
        for course in courses:
            Course.create_privacy(course=course)
        
        lectures = Lecture.objects.filter(privacy=None)
        for lecture in lectures:
            Lecture.create_privacy(lecture=lecture)
                
        self.stdout.write(self.style.SUCCESS("Done."))