import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth = JWTAuthentication()
        access_token = request.COOKIES.get('access_token')
        if access_token:
            try:
                validated_token = auth.get_validated_token(access_token)
                user = auth.get_user(validated_token)
                request.user = user
            except Exception:
                pass
