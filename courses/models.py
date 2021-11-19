from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from model_utils import Choices
UserModel = settings.AUTH_USER_MODEL


####### Quizes

class Quiz(models.Model):
    quiz_name = models.CharField(max_length=50)
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'quizzes'

    def __str__(self):
          return self.quiz_name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_title = models.TextField()

    def __str__(self):
          return self.question_title

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
          return f'{self.question}-{self.choice}'



class Category(models.Model):
    category_name = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

class Course(models.Model):

    title = models.CharField(max_length=100)
    description = models.TextField()
    categories = models.ManyToManyField(Category, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
          return self.title

    def can_access(self, user):
        if self.privacy.is_public():
            return True
        elif self.privacy.is_private():
            return False
        else:
            return user in self.privacy.shared_with.all()


class CoursePrivacy(models.Model):
    PRIVACY_CHOICES = Choices(
        ('public', 'Public'),
        ('private', 'Private'),
        ('custom', 'Custom'),
    )
    course = models.OneToOneField(Course, on_delete=models.CASCADE, blank=True, related_name="privacy")
    option = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default=PRIVACY_CHOICES.private)
    shared_with = models.ManyToManyField(UserModel, blank=True)

    def __str__(self):
          return self.course.title

    def is_public(self):
        return self.option == self.PRIVACY_CHOICES.public

    def is_private(self):
        return self.option == self.PRIVACY_CHOICES.private

    def is_custom(self):
        return self.option == self.PRIVACY_CHOICES.custom

class Attachement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attachements")
    file = models.FileField(upload_to='file')

    def __str__(self):
          return self.course.title


######### Course Content
class Content(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="content")
    title = models.CharField(max_length=100)
    video_content = models.CharField(blank=True, max_length=100)
    audio_content = models.CharField(blank=True, max_length=100)
    text_content = models.CharField(blank=True, max_length=100)
    order = models.IntegerField()
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ('order', )

    def __str__(self):
          return self.title

    def can_access(self, user):
        if self.privacy.is_public():
            return True
        elif self.privacy.is_private():
            return False
        else:
            return user in self.privacy.shared_with.all()



class ContentPrivacy(models.Model):
    PRIVACY_CHOICES = Choices(
        ('public', 'Public'),
        ('private', 'Private'),
        ('custom', 'Custom'),
    )

    content = models.OneToOneField(Content, on_delete=models.CASCADE, blank=True, related_name="privacy")
    option = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default=PRIVACY_CHOICES.private)
    shared_with = models.ManyToManyField(UserModel, blank=True)

    def __str__(self):
          return self.content.title

    def is_public(self):
        return self.option == self.PRIVACY_CHOICES.public

    def is_private(self):
        return self.option == self.PRIVACY_CHOICES.private

    def is_custom(self):
        return self.option == self.PRIVACY_CHOICES.custom

###### Course progress
class CourseProgress(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'course progress'

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.content.title}'

#### Comments and feedback

class Comment(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('published', 'Published'),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="comments")
    comment_body = models.TextField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)

    def __str__(self):
        return f'{self.user.email}-{self.comment_body}'

class Feedback(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="feedbacks")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.IntegerField(
    validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    description = models.TextField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_rating",
                check=models.Q(rating__range=(1, 5)),
            ),
        ]

    def __str__(self):
          return f'{self.user.email}-{self.course.title}'


### requests

class CorrectInfo(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    min_from = models.CharField(blank=True, max_length=100)
    min_to = models.CharField(blank=True, max_length=100)
    scientific_evidence = models.TextField(blank=True)

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.content.title}'


class Report(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.content.title}'
