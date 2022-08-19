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
        self.login_ip = ip
        try:
            geocoder_var = geocoder.ip(self.login_ip)
            self.country = geocoder_var.country
            self.city = geocoder_var.city
        except Exception as e:
            ip_info = self.get_ip_info()
            if not ip_info:
                self.country = "US"
                self.city = None
                
            if not ip_info["security"]["is_vpn"]:
                self.country = ip_info["country_code"]
                self.city = ip_info["city"]
            else:
                self.country = "US"
                self.city = None   
                
            
    def get_ip_info(self, timeout_sec=0.5):
        ip_geo_key = settings.IP_GEO_KEY
        url = settings.IP_GEO_URL.format(ip_geo_key, self.login_ip)
    
        try:
            r = requests.get(url=url, timeout=timeout_sec)
            if r.status_code != 200:
                return None
        except Exception as e:
            return None
    
        json_response = r.json()
        return json_response
