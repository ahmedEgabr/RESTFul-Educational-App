# Generated by Django 3.2.9 on 2022-07-29 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_courseprivacy_lectureprivacy'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CourseAttachement',
        ),
        migrations.DeleteModel(
            name='LectureAttachement',
        ),
    ]