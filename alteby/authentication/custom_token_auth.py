from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class CustomTokenAuth(TokenAuthentication):

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        
        if not user.is_student:
            raise exceptions.AuthenticationFailed('You are not a student to login.')

        student_profile = user.get_student_profile()
        if not student_profile:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        # TODO: to be added whrn add teacher role on app
        # if user.is_teacher:
        #     teacher_profile = user.get_teacher_profile()
        #     if teacher_profile:
        #         if not teacher_profile.is_active:
        #             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        return (user, token)
