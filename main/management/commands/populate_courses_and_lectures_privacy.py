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
            course.create_privacy()
        
        lectures = Lecture.objects.filter(privacy=None)
        for lecture in lectures:
            lecture.create_privacy()
                
        self.stdout.write(self.style.SUCCESS("Done."))
        