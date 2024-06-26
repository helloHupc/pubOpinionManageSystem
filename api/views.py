import uuid
import json
from django.views import View
from django.http import JsonResponse
from login.models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password



def generate_uuid():
    return uuid.uuid4()


class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print(data)
        username = data.get('username')
        password = data.get('password')

        check_user = UserProfile.objects.filter(username=username).first()
        print(check_user)

        if check_user is None:
            return JsonResponse({'msg': '用户不存在！'}, status=400)

        print(check_user.id)
        print(check_user.username)

        check_pwd = check_password(password, check_user.password)
        print(check_pwd)

        if check_pwd:
            new_uuid = generate_uuid()
            res_data = {'accessToken': new_uuid, 'userId': check_user.id}
            return JsonResponse({'msg': 'Login successful', 'data': res_data, 'code': 0})
        else:
            return JsonResponse({'msg': '账号或用户名错误！'}, status=400)


class UserInfoView(View):
    def get(self, request, user_id):
        check_user = UserProfile.objects.filter(id=user_id).first()
        print(check_user)

        if check_user is None:
            return JsonResponse({'msg': '用户不存在！'}, status=400)

        username = check_user.username
        user_id = check_user.id

        res_data = {
            'userId': user_id,
            'username': username,
            'avatar': 'https://hupc-blog-photo.oss-cn-beijing.aliyuncs.com/wp-content/uploads/2024/06/hacker.png',
            'roles': ["ROOT"]
        }

        return JsonResponse({'msg': 'success', 'data': res_data, 'code': 0})


class MenuRoutesView(View):
    def get(self, request):

        res_routes = [
            {
              'path': "/doc",
              'component': "Layout",
              'name': "/doc",
              'meta': {
                'title': "平台文档",
                'icon': "document",
                'hidden': False,
                'roles': ["ADMIN"],
              },
              'children': [
                {
                  'path': "internal-doc",
                  'component': "demo/internal-doc",
                  'name': "InternalDoc",
                  'meta': {
                    'title': "平台文档(内嵌)",
                    'icon': "document",
                    'hidden': False,
                    'roles': ["ADMIN"],
                  },
                },
                {
                  'path': "https://juejin.cn/post/7228990409909108793",
                  'name': "Https://juejin.cn/post/7228990409909108793",
                  'meta': {
                    'title': "平台文档(外链)",
                    'icon': "link",
                    'hidden': False,
                    'roles': ["ADMIN"],
                  },
                },
              ],
            },
            {
              'path': "/key-word",
              'component': "Layout",
              'name': "KeyWord",
              'redirect': "/key-word/page",
              'meta': {
                'title': "关键词",
                'icon': "document",
                'hidden': False,
                'roles': ["ADMIN"],
              },
              'children': [
                {
                  'path': "page",
                  'component': "key-word/page",
                  'name': "KeyWordPage",
                  'meta': {
                    'title': "关键词管理",
                    'icon': "document",
                    'hidden': False,
                    'roles': ["ADMIN"],
                  },
                },
              ],
            },
        ]

        return JsonResponse({'msg': 'success', 'data': res_routes, 'code': 0})



