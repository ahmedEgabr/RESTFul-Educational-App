from django.utils.deprecation import MiddlewareMixin
from alteby.utils import IPUtils, get_user_ip


class AssignUserGeoLocation(MiddlewareMixin):
    def process_request(self, request):
        user_ip = get_user_ip(request)
        if user_ip:
            ip_utils = IPUtils(ip=user_ip)
            request.country = ip_utils.country
            request.city = ip_utils.city
        else:
            request.country = None
            request.city = None
        return None
