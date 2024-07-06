from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from login.models import UserProfile
import api.utils

class UserIDValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        exempt_paths = ['/api/login']  # 如果有不需要验证的路径，可以在这里添加
        if request.path in exempt_paths:
            return None

        user_id_token = request.headers.get('UserToken')
        if not user_id_token:
            return JsonResponse({'msg': '无效请求'}, status=400)

        user_id = api.utils.decrypt_user_id(user_id_token)
        if not user_id:
            return JsonResponse({'msg': '无效请求'}, status=400)

        try:
            user = UserProfile.objects.get(id=user_id)
            request.user = user
        except UserProfile.DoesNotExist:
            return JsonResponse({'msg': '无效请求'}, status=401)

        return None
