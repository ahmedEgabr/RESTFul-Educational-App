# Generated by Django 3.2.9 on 2022-07-24 01:13

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_auto_20220723_0100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecture',
            name='text',
        ),
        migrations.AddField(
            model_name='lecture',
            name='objectives',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lecture',
            name='script',
            field=ckeditor.fields.RichTextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lecturereference',
            name='type',
            field=models.CharField(choices=[('website', 'Website'), ('book', 'Book'), ('link', 'Link'), ('paper', 'Paper'), ('journal', 'Journal'), ('article', 'Article')], max_length=20),
        ),
    ]
