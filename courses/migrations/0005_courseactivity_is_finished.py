# Generated by Django 3.2.9 on 2022-04-02 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_courseactivity_left_off_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseactivity',
            name='is_finished',
            field=models.BooleanField(default=False),
        ),
    ]
