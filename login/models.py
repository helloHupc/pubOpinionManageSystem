from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.


class UserProfile(AbstractUser):

    gender = (
        ('male', "男"),
        ('female', "女"),
    )

    username = models.CharField(max_length=128, unique=True)
    nickname = models.CharField(max_length=128, default="")
    password = models.CharField(max_length=256)
    avatar = models.CharField(max_length=256, default="")
    roles = models.CharField(max_length=128, default="")
    email = models.EmailField(max_length=32)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='userprofile_set',  # 添加related_name参数
        related_query_name='userprofile',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='userprofile_set',  # 添加related_name参数
        related_query_name='userprofile',
    )

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    UserProfile = models.OneToOneField('UserProfile', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.UserProfile.name + ":   " + self.code

    class Meta:

        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"