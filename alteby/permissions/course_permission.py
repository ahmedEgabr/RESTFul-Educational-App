import re
import alteby.utils as general_utils
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from courses.models import Course, Privacy
from django.conf import settings
from rest_framework.permissions import BasePermission

class CoursePermission(BasePermission):

    def has_permission(self, request, view):
        request_path = request.path[:-1] if request.path[-1] == "/" else request.path
        course_id = request_path.split("/")[3]
        allowed_courses = Course.get_allowed_courses(user=request.user)
        course = allowed_courses.filter(id=course_id).first()
        if not course:
            return False
        
        if not course.is_allowed_to_access_course(request.user):
            return False
        return True
        