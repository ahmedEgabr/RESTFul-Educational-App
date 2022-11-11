from django.db import models

class Student(models.Model):

    YEAR_IN_SCHOOL_CHOICES = [
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    ]
    ACADEMIC_YEAR = [
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third'),
        (4, 'Fourth'),
        (5, 'Fifth'),
        (6, 'Sixth'),
        (7, 'Seventh'),
    ]
    user = models.OneToOneField(
    "users.User",
    on_delete=models.CASCADE,
    primary_key=True,
    related_name="student_profile"
    )
    major = models.CharField(blank=True, null=True, max_length=40)
    academic_year = models.IntegerField(blank=True, null=True, choices=ACADEMIC_YEAR)
    year_in_school = models.CharField(max_length=20, blank=True, null=True, choices=YEAR_IN_SCHOOL_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    def is_enrolled(self, course):
        return course.id in self.user.enrollments.values_list('course', flat=True)

    def activate(self):
        if not self.is_active:
            self.is_active = False
            self.save()

    def deactivate(self):
        self.is_active = False
        self.save()
