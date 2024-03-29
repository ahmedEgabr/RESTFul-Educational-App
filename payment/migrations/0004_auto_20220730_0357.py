# Generated by Django 3.2.9 on 2022-07-30 01:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20220728_2312'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseenrollment',
            old_name='date_created',
            new_name='enrollment_date',
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created At'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='enrollment_duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='enrollment_duration_type',
            field=models.CharField(blank=True, choices=[('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], max_length=10),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='is_enrolled_for_life_long',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
    ]
