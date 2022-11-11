# Generated by Django 3.2.9 on 2022-08-07 18:50

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0020_remove_course_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursePlanPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(blank=True, choices=[('dollar', '$ Dollar'), ('egp', 'E£ EGP')], default='dollar', max_length=10, null=True)),
                ('countries', django_countries.fields.CountryField(blank=True, max_length=746, multiple=True)),
                ('select_all_countries', models.BooleanField(default=False, help_text='<small class="text-warning">&#x26A0; When ckecked, all other prices is going to be deactivated.</small>')),
                ('is_free_for_selected_countries', models.BooleanField(default=False)),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True, help_text='<small class="text-warning">&#x26A0; When not ckecked, this price will not be visable to the students.</small>')),
            ],
        ),
        migrations.CreateModel(
            name='CoursePricingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('duration_type', models.CharField(blank=True, choices=[('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], max_length=10, null=True)),
                ('lifetime_access', models.BooleanField(default=False)),
                ('is_free_for_all_countries', models.BooleanField(default=False, help_text='<small class="text-warning">&#9888; When checked, all plan prices is going to be deactivated.</small>')),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True, help_text='<small class="text-warning">&#x26A0; When not ckecked, this price will not be visable to the students.</small>')),
            ],
            options={
                'verbose_name_plural': 'Courses Pricing Plans',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='course',
            name='is_free',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='language',
            field=models.CharField(choices=[('arabic', 'Arabic'), ('english', 'English'), ('arabic_english', 'Arabic/English')], default='arabic', max_length=20),
        ),
        migrations.DeleteModel(
            name='CoursePrice',
        ),
        migrations.AddField(
            model_name='coursepricingplan',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricing_plans', to='courses.course'),
        ),
        migrations.AddField(
            model_name='coursepricingplan',
            name='created_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_coursepricingplans', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coursepricingplan',
            name='updated_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='updated_coursepricingplans', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='courseplanprice',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='courses.coursepricingplan'),
        ),
        migrations.AlterUniqueTogether(
            name='coursepricingplan',
            unique_together={('course', 'duration', 'duration_type')},
        ),
    ]
