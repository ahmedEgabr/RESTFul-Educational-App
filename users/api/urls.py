from django.urls import path, include
from payment.api.views import CoursesEnrollments
from .views import (
SignIn, SignUp,
ProfileDetail, EnrolledCourses,
ChangePasswordView,
ResetPasswordConfirmView,
DeactivateUserView,
UserScreenShotRecordView,
AnonymousToken
)

app_name = 'users'

urlpatterns = [
    # users APIs routes
    path('<int:user_id>/enrollments', CoursesEnrollments.as_view(), name="courses_enrollments"),
    path('<int:user_id>/deactivate', DeactivateUserView.as_view(), name="deactivate"),
    path('<int:user_id>/record-screenshot', UserScreenShotRecordView.as_view(), name="record-screenshot"),
    path('profile/', ProfileDetail.as_view(), name="profile"),
    path('<int:user_id>/enrolled-courses/', EnrolledCourses.as_view(), name="enrolled-courses"),
    path('anonymous-token', AnonymousToken.as_view(), name="anonymous-token"),

    # Authentication Routes
    path('signin', SignIn.as_view(), name="signin"),
    path('signup', SignUp.as_view(), name="singup"),

    # Change Password
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    # Reset Password
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # Change Password
    path('reset-password/confirm/', ResetPasswordConfirmView.as_view(), name='reset-password'),

  ]
