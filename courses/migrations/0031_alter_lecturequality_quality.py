# Generated by Django 3.2.9 on 2022-10-13 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0030_coursesgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecturequality',
            name='quality',
            field=models.IntegerField(choices=[(2160, '2160p'), (1440, '1440p'), (1080, '1080p'), (720, '720p'), (480, '480p'), (360, '360p'), (240, '240p'), (144, '144p')]),
        ),
    ]