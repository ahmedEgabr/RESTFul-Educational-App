from django.contrib import admin
from alteby.admin_sites import main_admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, Student, Teacher
from django.contrib.auth.forms import (
    AdminPasswordChangeForm
)
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.contrib import messages


class UserConfig(UserAdmin):
    model = User
    change_password_form = AdminPasswordChangeForm
    actions = ["activate_selected_users", "deactivate_selected_users"]
    list_filter = ('email', 'username', 'is_active', 'is_staff')
    ordering = ('-date_joined',)
    list_display = ('email', 'username',
                    'is_active', 'is_staff')
    readonly_fields = ["date_joined"]

    fieldsets = (
        ("User Information", {'fields': ('email', 'username', 'password', 'screenshots_taken')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_student', 'is_teacher', 'is_superuser', 'groups', 'user_permissions')}),
    )

    def activate_selected_users(self, request, queryset):
        queryset = queryset.prefetch_related("teacher_profile", "student_profile")
        for user in queryset:
            if user.activate():
                message = "User: {0} successfully activated.".format(user.username)
                self.message_user(request, message, level=messages.SUCCESS)
            else:
                message = "Cannot activate user: {0}.".format(user.username)
                self.message_user(request, message, level=messages.ERROR)
        return

    def deactivate_selected_users(self, request, queryset):
        queryset = queryset.prefetch_related("teacher_profile", "student_profile")
        for user in queryset:
            if user.deactivate():
                message = "User: {0} successfully deactivated.".format(user.username)
                self.message_user(request, message, level=messages.SUCCESS)
            else:
                message = "Cannot deactivate user: {0}.".format(user.username)
                self.message_user(request, message, level=messages.ERROR)
        return


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
main_admin.register(Group, GroupAdmin)
