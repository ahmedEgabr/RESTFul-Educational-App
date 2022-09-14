# Generated by Django 3.2.9 on 2022-09-09 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_auto_20220909_2354'),
        ('payment', '0007_alter_courseenrollment_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='promoter',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_promoter': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrollments_contributions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='source_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.sourcegroup'),
        ),
    ]