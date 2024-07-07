from django.contrib import admin
from .models import KeyWord, BlogInfo


class BlogInfoAdmin(admin.ModelAdmin):
    list_display = ('blog_id', 'key_word', 'author_name', 'blog_url', 'blog_content', 'c_time')  # 这里填入你想在后台显示的字段
    search_fields = ('key_word', 'author_name')  # 使这些字段可搜索
    list_filter = ('blog_url',)  # 可以按这些字段过滤


admin.site.register(KeyWord)
admin.site.register(BlogInfo)
