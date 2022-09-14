from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from .constants import TEACHER_GROUP, STUDENT_GROUP
from django.db.models import Q

class MainAdmin(AdminSite):

    enable_nav_sidebar = False
    login_template = 'admin/login.html'

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        allowed_groups = []

        if hasattr(request.user, "is_blocked"):
            if request.user.is_blocked:
                return False

        is_allowed = request.user.groups.filter(name__in=allowed_groups).exists()
        if not (request.user.is_active and request.user.is_superuser or is_allowed):
            return False
        return True


class MainAdminConfig(AdminConfig):
    default_site = 'alteby.admin_sites.MainAdmin'

main_admin = MainAdmin(name="admin")


class TeacherAdmin(AdminSite):
    site_header = ("Teacher Panel")
    site_title = ("Teacher Panel")
    index_title = ("Medical Mentor Teacher Panel")
    enable_nav_sidebar = True

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        user = request.user

        if hasattr(user, "is_blocked"):
            if user.is_blocked:
                return False

        if not user.is_active:
            return False

        if not user.groups.filter(name=TEACHER_GROUP).exists():
            return False
        teacher_profile = user.get_teacher_profile()
        if not teacher_profile:
            return False
        return True


teacher_admin = TeacherAdmin(name="teacher_admin")


class PromoterAdmin(AdminSite):
    site_header = ("Promoter Panel")
    site_title = ("Promoter Panel")
    index_title = ("Medical Mentor Teacher Panel")
    enable_nav_sidebar = True

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        user = request.user

        if hasattr(user, "is_blocked"):
            if user.is_blocked:
                return False

        if not user.is_active:
            return False

        if not request.user.is_promoter:
            return False
        return True


promoter_admin = PromoterAdmin(name="promoter_admin")
