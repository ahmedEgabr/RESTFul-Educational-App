# Generated by Django 3.2.9 on 2022-01-21 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_alter_content_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='duration',
        ),
    ]
