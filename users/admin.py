from django.contrib import admin
from alteby.admin_sites import main_admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, Student, Teacher
from django.contrib.auth.forms import (
    AdminPasswordChangeForm
)

class UserConfig(UserAdmin):
    model = User
    change_password_form = AdminPasswordChangeForm

    list_filter = ('email', 'username', 'is_active', 'is_staff')
    ordering = ('-date_joined',)
    list_display = ('email', 'username',
                    'is_active', 'is_staff')

    fieldsets = (
        ("User Information", {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_student', 'is_teacher', 'is_superuser', 'groups', 'user_permissions')}),
    )

class StudentConfig(admin.ModelAdmin):
    model = Student

    list_filter = ('user', 'major', 'academic_year', 'year_in_school')
    list_display = ('user', 'major', 'academic_year', 'year_in_school')

    fieldsets = (
        ("Student Account", {'fields': ('user', )}),
        ('Status', {'fields': ('is_active', )}),
        ('Education', {'fields': ('major', 'academic_year', 'year_in_school')}),
    )

class TeacherConfig(admin.ModelAdmin):
    model = Teacher

    list_filter = ('major', )
    list_display = ('user', 'major')

    fieldsets = (
        ("Teacher Account", {'fields': ('user', )}),
        ('Status', {'fields': ('is_active', )}),
        ('Information', {'fields': ('major',)}),
    )


# Register your models here.
main_admin.register(User, UserConfig)
main_admin.register(Student, StudentConfig)
main_admin.register(Teacher, TeacherConfig)
