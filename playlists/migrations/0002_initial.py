# Generated by Django 3.2.9 on 2021-11-20 06:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('playlists', '0001_initial'),
        ('courses', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Playlists', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favorite',
            name='content',
            field=models.ManyToManyField(blank=True, to='courses.Content'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='playlist',
            unique_together={('owner', 'name')},
        ),
    ]
