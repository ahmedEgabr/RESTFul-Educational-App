# Generated by Django 3.2.9 on 2022-07-24 06:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_referencecategory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0011_lectureexternallink_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('website', 'Website'), ('book', 'Book'), ('link', 'Link'), ('paper', 'Paper'), ('journal', 'Journal'), ('article', 'Article')], max_length=20)),
                ('link', models.URLField(blank=True)),
                ('categories', models.ManyToManyField(blank=True, to='categories.ReferenceCategory')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_references', to=settings.AUTH_USER_MODEL)),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='updated_references', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='LectureReference',
        ),
        migrations.AddField(
            model_name='lecture',
            name='references',
            field=models.ManyToManyField(blank=True, to='courses.Reference'),
        ),
    ]