from django.contrib.admin import AdminSite

class TeacherAdmin(AdminSite):
    site_header = ("Teacher Panel")
    site_title = ("Teacher Panel")
    index_title = ("Emtyaz Advizor Teacher Panel")
    enable_nav_sidebar = False

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        user = request.user
        if not user.groups.filter(name="Teachers").exists():
            return False
        teacher_profile = user.get_teacher_profile()
        if not teacher_profile:
            return False
        return True


teacher_admin = TeacherAdmin(name="teacher_admin")
