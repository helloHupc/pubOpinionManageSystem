from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import forms
import hashlib
import datetime
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views import View
import json
from django.views.decorators.csrf import ensure_csrf_cookie
import uuid

def generate_uuid():
    return uuid.uuid4()


@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')


def login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    encrypt_password = hash_code(password)

    check_user_info = models.User.objects.filter(name=username).values().first()
    if not check_user_info or encrypt_password != check_user_info['password']:
        return api_response("用户名或者密码错误！", 110001)

    token = generate_uuid()
    return api_response("登录成功！", 200, '', token)


# 用户注册
def register(request):
    data = json.loads(request.body)
    username = data.get('username')
    password1 = data.get('password1')
    password2 = data.get('password2')
    email = data.get('email')

    if password1 != password2:
        return api_response("两次输入的密码不同", 100001)

    same_name_user = models.User.objects.filter(name=username)
    if same_name_user:
        return api_response("用户名已经存在", 100002)

    same_email_user = models.User.objects.filter(email=email)
    if same_email_user:
        return api_response("该邮箱已经被注册了！", 100003)

    new_user = models.User()
    new_user.name = username
    new_user.password = hash_code(password1)
    new_user.email = email
    new_user.save()

    code = make_confirm_string(new_user)
    # send_email(email, code)
    return api_response("请前往邮箱进行确认！", 200)


def api_response(message, code, data='', token=''):
    re_data = {
        'message': message,
        'code': code,
    }
    if data:
        re_data['data'] = data
    if token:
        re_data['token'] = token

    return JsonResponse(re_data)


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()
    return redirect("/login/")


def hash_code(s, salt='pubOpinionManageSystem'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user,)
    return code


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives

    subject = '来自pubOpinionManageSystem的注册确认邮件'

    text_content = '''这是pubOpinionManageSystem的确认邮件内容\
    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.hupc.site</a>，\
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())
