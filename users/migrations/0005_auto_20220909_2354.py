# Generated by Django 3.2.9 on 2022-09-09 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='is_promoter',
            field=models.BooleanField(default=False, verbose_name='Promoter status'),
        ),
    ]
