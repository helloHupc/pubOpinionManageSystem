import base64
from django.conf import settings
from django.http import JsonResponse


def encrypt_user_id(user_id):
    print('user_id', user_id)
    key = settings.API_SECRET_KEY.encode()
    print('key',key)
    encoded_user_id = str(user_id).encode()
    encrypted_user_id = base64.urlsafe_b64encode(encoded_user_id + key)
    return encrypted_user_id.decode()


def decrypt_user_id(encrypted_user_id):
    key = settings.API_SECRET_KEY.encode()
    decoded_user_id = base64.urlsafe_b64decode(encrypted_user_id.encode())
    user_id = decoded_user_id.replace(key, b'').decode()
    return user_id


def api_return_success(data):
    return JsonResponse({'msg': 'successful', 'data': data, 'code': 0})


def api_return_error(msg, code):
    return JsonResponse({'msg': msg, 'data': {}, 'code': code})
