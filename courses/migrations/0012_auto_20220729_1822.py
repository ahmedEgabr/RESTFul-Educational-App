# Generated by Django 3.2.9 on 2022-07-29 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_auto_20220729_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privacy',
            name='available_from',
            field=models.DateTimeField(blank=True, help_text='Must be set when choosing public (for a limited period) option.', null=True),
        ),
        migrations.AlterField(
            model_name='privacy',
            name='enrollment_period',
            field=models.IntegerField(blank=True, help_text='\n    The period that the course will be availabe for the user form the date of the enrollment when the course was free.\n    Must be set when choosing public (for limited period) option.\n    ', null=True, verbose_name='When avilable for free, users can enroll it for'),
        ),
        migrations.AlterField(
            model_name='privacy',
            name='enrollment_period_type',
            field=models.CharField(blank=True, choices=[('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], help_text='Must be set when choosing public (for a limited period) option.', max_length=10),
        ),
        migrations.AlterField(
            model_name='privacy',
            name='option',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('shared', 'Shared'), ('limited_period', 'Public (for a Limited Period)')], default='private', max_length=15),
        ),
        migrations.AlterField(
            model_name='privacy',
            name='period',
            field=models.IntegerField(blank=True, help_text='Must be set when choosing public (for a limited period) option.', null=True),
        ),
        migrations.AlterField(
            model_name='privacy',
            name='period_type',
            field=models.CharField(blank=True, choices=[('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], help_text='Must be set when choosing public (for a limited period) option.', max_length=10),
        ),
    ]