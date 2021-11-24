# Generated by Django 3.2.9 on 2021-11-24 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_student_academic_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='academic_year',
            field=models.IntegerField(blank=True, choices=[(1, 'FIRST'), (2, 'SECOND'), (3, 'THIRD'), (4, 'FOURTH'), (5, 'FIFTH'), (6, 'SIXTH'), (7, 'SEVENTH')], null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='major',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='year_in_school',
            field=models.CharField(blank=True, choices=[('FR', 'Freshman'), ('SO', 'Sophomore'), ('JR', 'Junior'), ('SR', 'Senior'), ('GR', 'Graduate')], max_length=20, null=True),
        ),
    ]
