from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

ALLOWED_REFERER = 'https://10.11.4.10'

class BlockExternalRequestsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        referer = request.META.get('HTTP_REFERER', '')

        # `HTTP_REFERER` başlığını kontrol ederek sadece belirli bir referans siteyi kabul et
        if referer and not referer.startswith(ALLOWED_REFERER):
            return HttpResponseForbidden("Requests from this referer are not allowed.")

        return None
