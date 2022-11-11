from rest_framework.response import Response
from rest_framework.views import APIView
from main.models import ContactUs
from main.models import AppVersion, AppStatus
from .serializers import ContactUsSerializer


class ContactUsView(APIView):

    permission_classes = ()

    def get(self, request):
        contact_info = ContactUs.objects.first()
        serializer = ContactUsSerializer(contact_info, many=False)
        return Response(serializer.data)


class AppVersionView(APIView):

    permission_classes = ()

    def get(self, request):
        response = {}

        version_name_str = request.query_params.get("version_name", None)
        if version_name_str:

            version_code = AppVersion.convert_version_name_to_code(version_name_str)
            is_force_upgrade = AppVersion.is_force_upgrade(version_code)
            is_recommend_upgrade = AppVersion.is_recommend_upgrade(version_code)

            response["is_force_upgrade"] = is_force_upgrade
            response["is_recommend_upgrade"] = is_recommend_upgrade
        else:
            response["is_force_upgrade"] = False
            response["is_recommend_upgrade"] = False

        app_status = AppStatus.objects.first()
        if app_status:
            response["is_online"] = app_status.is_online
            response["is_under_maintenance"] = app_status.is_under_maintenance
            response["reason"] = app_status.reason
            response["downtime_till"] = app_status.downtime_till
        else:
            response["is_online"] = False
            response["is_under_maintenance"] = False
            response["reason"] = ""
            response["downtime_till"] = None

        return Response(response, status=200)
