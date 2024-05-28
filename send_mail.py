# 测试邮件发送文件
import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'login_register.settings'

if __name__ == '__main__':
    send_mail(
        'django login_register测试邮件',
        '这是测试内容',
        'xxx@qq.com',
        ['xxx@163.com'],
    )