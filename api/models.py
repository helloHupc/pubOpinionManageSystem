from django.db import models
from login.models import UserProfile
from django.utils import timezone


class KeyWord(models.Model):
    key_word = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    status = models.IntegerField(default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)
    u_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key_word

    def save(self, *args, **kwargs):
        if not self.id:
            self.u_time = self.c_time
        super(KeyWord, self).save(*args, **kwargs)

    class Meta:

        ordering = ["-c_time", "-u_time"]
        verbose_name = "关键词"
        verbose_name_plural = "关键词"


class BlogInfo(models.Model):
    blog_id = models.CharField(max_length=256)
    key_word = models.CharField(max_length=256, default='')
    key_word_id = models.CharField(max_length=256, default='')
    author_name = models.CharField(max_length=256)
    author_id = models.CharField(max_length=256)
    blog_url = models.CharField(max_length=256, default='')
    like_count = models.CharField(max_length=256, default='')
    publish_time = models.CharField(max_length=256)
    blog_content = models.TextField(null=True, blank=True)
    sentiment = models.CharField(max_length=256, default='')
    type = models.CharField(max_length=30, default='weibo')
    c_time = models.DateTimeField(auto_now_add=True)
    u_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.blog_content

    class Meta:

        ordering = ["-c_time", "-u_time"]
        verbose_name = "微博博文"
        verbose_name_plural = "微博博文"
