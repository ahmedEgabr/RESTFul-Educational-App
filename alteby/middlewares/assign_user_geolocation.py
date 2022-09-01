from django.utils.deprecation import MiddlewareMixin
from alteby.utils import IPUtils, get_user_ip
from django.conf import settings


class AssignUserGeoLocation(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__name__ not in getattr(settings, "IP_GEO_WHITELISTED_VIEWS", []):
            return None
        
        user_ip = get_user_ip(request)
        if user_ip:
            ip_utils = IPUtils(ip=user_ip)
            request.country = ip_utils.country
            request.city = ip_utils.city
        else:
            request.country = "US"
            request.city = None
        return None
