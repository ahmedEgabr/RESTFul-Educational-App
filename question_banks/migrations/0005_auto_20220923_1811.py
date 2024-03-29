# Generated by Django 3.2.9 on 2022-09-23 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0029_auto_20220923_1811'),
        ('question_banks', '0004_rename_questionresult_questionanswer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='image',
            new_name='explanation_image',
        ),
        migrations.AddField(
            model_name='question',
            name='reference',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='questionanswer',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='courses.quiz'),
        ),
    ]
