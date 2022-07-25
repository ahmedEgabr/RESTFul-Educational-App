import os
import inspect
import requests
import geocoder
from django.conf import settings


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    elif x_real_ip:
        ip = x_real_ip
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class IPUtils:
    """ IP Utils class """

    def __init__(self, ip):
        self.ip = geocoder.ip(ip)

    @property
    def country(self):
        return self.ip.country

    @property
    def city(self):
        return self.ip.city
    #
    # @classmethod
    # def get_ip_info(cls, login_ip, timeout_sec=0.5):
    #     ip_geo_key = settings.IP_GEO_KEY
    #     url = "https://ipgeolocation.abstractapi.com/v1/?api_key={0}&ip_address={1}".format(ip_geo_key,login_ip)
    #
    #     try:
    #         r = requests.get(url=url, timeout=timeout_sec)
    #         if r.status_code != 200:
    #             message = "abstract ip geo status code: {0}. \nbody: {1}".format(r.status_code, r.text)
    #             exception_log(logger_name="requests", filename=os.path.basename(__file__),
    #                           message=message, line_no=inspect.stack()[0][2])
    #             return None
    #     except Exception as e:
    #         message = "IP geo error: \n{0}".format(e)
    #         exception_log(logger_name="requests", filename=os.path.basename(__file__),
    #                       message=message, line_no=inspect.stack()[0][2])
    #         return None
    #
    #     json_response = r.json()
    #     message = "abstract ip geo response: {0}".format(r.json())
    #     debug_log(logger_name="requests", filename=os.path.basename(__file__),
    #               message=message, line_no=inspect.stack()[0][2])
    #
    #     return json_response
