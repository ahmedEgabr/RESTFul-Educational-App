from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework import renderers
from rest_framework import parsers
from .serializers import AuthTokenSerializer, SignUpSerializer, StudentSerializer, ChangePasswordSerializer
from django.core.exceptions import ValidationError
from users.models import Student
from courses.api.serializers import CourseSerializer
from users.models import User
from rest_framework.permissions import IsAuthenticated
from django_rest_passwordreset.views import ResetPasswordConfirm
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import pre_password_reset, post_password_reset
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django_rest_passwordreset.serializers import ResetTokenSerializer
from django.conf import settings
from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import login
from alteby.utils import success as success_response
from utility import encode_data


class SignIn(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            if not created:
                token.delete()
                token, created = Token.objects.get_or_create(user=user)
                
            encoded_token = encode_data({
                "id": user.id
            })
            response = {
                'token': token.key,
                'encoded_token': encoded_token,
                'user_id': user.pk,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'year_in_school': user.student_profile.year_in_school,
                'academic_year': user.student_profile.academic_year,
                'major': user.student_profile.major
            }

            return Response(response)
        except:
            response = {}
            errors = serializer.errors
            for error in errors:
                response[error] = errors[error][0]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class SignUp(APIView):
    permission_classes = ()
    def post(self, request, format=True):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            token, created = Token.objects.get_or_create(user=user)
            encoded_token = encode_data({
                "id": user.id
            })
            
            response = {
                'token': token.key,
                'encoded_token': encoded_token,
                'user_id': user.pk,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'year_in_school': user.student_profile.year_in_school,
                'academic_year': user.student_profile.academic_year,
                'major': user.student_profile.major
            }
        else:
            response = serializer.errors
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_201_CREATED)


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(ResetPasswordConfirm):

    def get(self, request):
        token = request.GET.get('token', None)
        data = {'token': token}

        try:
            if not token:
                raise Exception("Invalid Link.")
            serializer = ResetTokenSerializer(data=data)
            serializer.is_valid(raise_exception=False)
            return render(request, 'users/reset_password_confirm.html')
        except Exception as e:
            context = {
            'error_message': 'This link may be invalid or expired.'
            }
            return render(request, 'users/reset_password_error.html', context)



    def post(self, request, *args, **kwargs):
        data = {
        'token': request.GET.get('token'),
        'password': request.data['password']
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        token = serializer.validated_data['token']

        # find token
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()

        # change users password (if we got to this code it means that the user is_active)
        if reset_password_token.user.eligible_for_reset():
            pre_password_reset.send(sender=self.__class__, user=reset_password_token.user)
            try:
                # validate the password against existing validators
                validate_password(
                    password,
                    user=reset_password_token.user,
                    password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
                )
            except ValidationError as e:
                # raise a validation error for the serializer
                return render(request, 'users/reset_password_confirm.html', context={
                 'error_messages': e.messages
                })


            reset_password_token.user.set_password(password)
            reset_password_token.user.save()
            post_password_reset.send(sender=self.__class__, user=reset_password_token.user)

        # Delete all password reset tokens for this user
        ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

        return render(request, 'users/reset_password_done.html')


class ProfileDetail(APIView):

    def get(self, request):
        student = Student.objects.select_related('user').get(user=request.user)
        serializer = StudentSerializer(student, many=False)
        context = serializer.data
        return Response(serializer.data)

class EnrolledCourses(APIView, PageNumberPagination):

    def get(self, request, user_id):

        enrolled_courses = request.user.get_enrolled_courses()
        if enrolled_courses:
            enrolled_courses = enrolled_courses.prefetch_related(
                'tags', 'privacy__shared_with'
                ).select_related(
                    'privacy'
                    ).all()

        enrolled_courses = self.paginate_queryset(enrolled_courses, request, view=self)
        serializer = CourseSerializer(enrolled_courses, many=True, context={'request':request})
        return self.get_paginated_response(serializer.data)

class DeactivateUserView(APIView):

    def get(self, request, user_id):
        request.user.deactivate()
        return Response(success_response("account_deactivated"), status=status.HTTP_200_OK)

class UserScreenShotRecordView(APIView):
    def get(self, request, user_id):
        user = request.user
        user.record_a_screenshot()
        response = {
        "is_blocked": user.is_reached_screenshots_limit
        }
        return Response(response, status=status.HTTP_200_OK)

class AnonymousToken(APIView):

    authentication_classes = ()
    permission_classes = ()

    def get(self, request):

        anonymous_user = User.get_or_create_anonymous_user()
        token, created = Token.objects.get_or_create(user=anonymous_user)
        encoded_token = encode_data({
                "id": anonymous_user.id
            })
        response = {
            'token': token.key,
            'encoded_token': encoded_token
        }
        return Response(response, status=status.HTTP_200_OK)
