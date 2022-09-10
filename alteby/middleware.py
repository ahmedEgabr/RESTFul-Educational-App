import re
import alteby.utils as general_utils
from django.db.models import Q
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, reverse
from django.http import JsonResponse
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.response import Response
from courses.models import Course, Privacy
from courses.utils import get_object
from courses.utils import get_object
from django.conf import settings
from re import sub
from rest_framework.authtoken.models import Token


class CoursePermissionMiddleware(MiddlewareMixin):

    @permission_classes([IsAuthenticated])
    def process_request(self, request):
        assert hasattr(request, 'user'), "None"

        request_path = request.path[:-1] if request.path[-1] == "/" else request.path
        course_path_regix = "^/api/courses\/([0-9]+)(?=[^\/]*)"
        if re.match(course_path_regix, request_path):
            
            if self.is_index_requested(request_path):
                return None
            
            course_id = request_path.split("/")[3]
            header_token = request.META.get('HTTP_AUTHORIZATION', None)
            if header_token is not None:
              try:
                token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
                token_obj = Token.objects.get(key = token)
                request.user = token_obj.user
              except Token.DoesNotExist:
                return JsonResponse(general_utils.error('page_access_denied'), status=401)

            course = Course.objects.filter(
                id=course_id,
                is_active=True
            ).exclude(
                Q(assigned_topics__topic__unit__course__privacy__option=Privacy.PRIVACY_CHOICES.shared) &
                ~Q(assigned_topics__topic__unit__course__privacy__shared_with__in=[request.user])
            )
            if not course:
                return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)
            
            if not course.is_allowed_to_access_course(request.user):
                return JsonResponse(general_utils.error('access_denied'), status=403)

    def is_index_requested(self, request_path):

        course_path_regix = "^/api/courses\/([0-9]+)(?=[^\/]*)/index$"
        if not re.match(course_path_regix, request_path):
            return False
        return True
