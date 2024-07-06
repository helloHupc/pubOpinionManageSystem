import uuid
import json
from django.views import View
from django.http import JsonResponse
from login.models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.utils import encrypt_user_id, api_return_error, api_return_success
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from api.models import KeyWord, BlogInfo
from django.core.serializers import serialize
import requests
from lxml import etree
import csv
import re
import time
import random
from html.parser import HTMLParser


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
            return api_return_error('用户不存在！', 100001)

        print(check_user.id)
        print(check_user.username)

        check_pwd = check_password(password, check_user.password)
        print(check_pwd)

        if check_pwd:
            new_uuid = generate_uuid()
            user_id_token = encrypt_user_id(check_user.id)
            res_data = {'accessToken': new_uuid, 'userToken': user_id_token}
            return api_return_success(res_data)
        else:
            return api_return_error('账号或用户名错误！', 100002)


class UserInfoView(View):
    def get(self, request, user_id):
        check_user = UserProfile.objects.filter(id=user_id).first()
        print(check_user)

        if check_user is None:
            return api_return_error('用户不存在！', 100003)

        username = check_user.username
        user_id = check_user.id

        res_data = {
            'userId': user_id,
            'username': username,
            'avatar': 'https://hupc-blog-photo.oss-cn-beijing.aliyuncs.com/wp-content/uploads/2024/06/hacker.png',
            'roles': ["ROOT"]
        }

        return api_return_success(res_data)


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
            {
                'path': "/data-manage",
                'component': "Layout",
                'name': "DataManage",
                'redirect': "/data-manage/page",
                'meta': {
                    'title': "数据管理",
                    'icon': "document",
                    'hidden': False,
                    'roles': ["ADMIN"],
                },
                'children': [
                    {
                        'path': "page",
                        'component': "data-manage/page",
                        'name': "DataManagePage",
                        'meta': {
                            'title': "数据管理",
                            'icon': "document",
                            'hidden': False,
                            'roles': ["ADMIN"],
                        },
                    },
                ],
            },
        ]

        return api_return_success(res_routes)


class KeyWordView(View):
    def post(self, request, action):
        if action == 'add':
            # 添加关键词
            return self.add(request)
        elif action == 'get_list':
            # 获取列表
            return self.get_list(request)
        elif action == 'get_info':
            # 获取单条数据
            return self.get_info(request)
        elif action == 'delete':
            return self.delete(request)
        elif action == 'update':
            return self.update(request)
        elif action == 'get_key_word_list':
            return self.get_key_word_list(request)
        else:
            return api_return_error('请求错误！', 100004)

    def add(self, request):
        user = request.user
        if user is None:
            return api_return_error('数据异常！', 100005)

        data = json.loads(request.body)

        try:
            user_profile = UserProfile.objects.get(id=user.id)
        except UserProfile.DoesNotExist:
            return api_return_error('用户不存在！', 100006)

        key_word = data['key_word']
        if KeyWord.objects.filter(key_word=key_word).exists():
            return api_return_error('关键词已存在！', 100007)

        data['user_id'] = user_profile.id
        print('data', data)
        res = KeyWord.objects.create(**data)

        if res.id is None:
            return api_return_error('添加失败！', 100008)

        res_data = {
            'id': res.id
        }

        return api_return_success(res_data)

    def get_list(self, request):
        data = json.loads(request.body)
        print('data',data)

        page = data.get('pageNum', 1)
        page_size = data.get('pageSize', 10)
        keywords = data.get('keywords')

        if keywords is not None:
            # 使用 icontains 进行模糊查询
            keywordList = KeyWord.objects.filter(key_word__icontains=keywords)
        else:
            keywordList = KeyWord.objects.all()

        paginator = Paginator(keywordList, page_size)

        try:
            keywords_page = paginator.page(page)
        except PageNotAnInteger:
            keywords_page = paginator.page(1)
        except EmptyPage:
            keywords_page = paginator.page(paginator.num_pages)

        data_list = []
        for keyword in keywords_page:
            data_list.append({
                'id': keyword.id,
                'key_word': keyword.key_word,
                'description': keyword.description,
                'status': keyword.status,
                'user_id': keyword.user_id,
                'nickname': keyword.user.nickname,
                'createTime': keyword.c_time.strftime('%Y-%m-%d %H:%M:%S'),
                'updateTime': keyword.u_time.strftime('%Y-%m-%d %H:%M:%S'),
            })
        res_data = {
            'total': paginator.count,
            'pageNum': keywords_page.number,
            'pageSize': page_size,
            'list': data_list
        }

        return api_return_success(res_data)


    def get_info(self, request):
        data = json.loads(request.body)
        print('data', data)

        id = data.get('id')
        if id is None:
            return api_return_error('数据异常！', 100009)

        # 使用 get 方法查询单条数据
        try:
            keyword = KeyWord.objects.get(id=id)
            res_data = {
                'id': keyword.id,
                'key_word': keyword.key_word,
                'description': keyword.description,
                'status': int(keyword.status),
                'user_id': keyword.user_id,  # assuming user_id is a foreign key
                'c_time': keyword.c_time,
                'u_time': keyword.u_time
            }
        except KeyWord.DoesNotExist:
            return api_return_error('数据获取失败！', 100010)

        return api_return_success(res_data)

    def delete(self, request):
        data = json.loads(request.body)
        print('data', data)

        ids = data.get('ids')
        print('ids', ids)
        if ids is None:
            return api_return_error('数据异常！', 100011)

        # 将 ids 字符串转换为列表
        ids_list = ids.split(',')

        # 使用 filter 和 delete 方法批量删除
        KeyWord.objects.filter(id__in=ids_list).delete()
        return api_return_success({})

    def update(self, request):
        data = json.loads(request.body)
        print('data', data)

        id = data.get('id')
        if id is None:
            return api_return_error('数据异常！', 100012)

        try:
            # 获取要更新的对象
            keyword = KeyWord.objects.get(id=id)

            keyword.key_word = data.get('key_word', keyword.key_word)
            keyword.description = data.get('description', keyword.description)
            keyword.status = data.get('status', keyword.status)

            # 保存对象
            keyword.save()
            return api_return_success({})

        except KeyWord.DoesNotExist:
            return api_return_error('更新失败！', 100013)

    def get_key_word_list(self, request):
        keywordList = KeyWord.objects.all()

        if keywordList is None:
            return api_return_error('数据异常！', 100014)

        res_data = [
            {
                "value": keyword.id,
                "label": keyword.key_word
            }
            for keyword in keywordList
        ]

        return api_return_success(res_data)


class CrawlerView(View):
    def post(self, request, action):
        if action == 'crawl_data_by_key_word':
            # 根据关键词获取微博爬虫数据
            return self.crawl_data_by_key_word(request)
        elif action == 'get_blog_list':
            # 获取列表
            return self.get_blog_list(request)
        else:
            return api_return_error('请求错误！', 110001)


    def crawl_data_by_key_word(self, request):
        data = json.loads(request.body)
        print('data', data)
        key_word_id = data['keywords']

        try:
            key_word_info = KeyWord.objects.get(id=key_word_id)
            key_word = key_word_info.key_word

        except KeyWord.DoesNotExist:
            return api_return_error('数据获取失败！', 110002)

        baseUrl = 'https://s.weibo.com/weibo?q=%23{}%23&Refer=index'
        url = baseUrl.format(key_word)
        print(url)
        self.get_weibo_topic(url, key_word, key_word_id)
        return api_return_success({})

    def get_weibo_topic(self, url, key_word, key_word_id):
        headers_com = {
            'Cookie': 'UOR=www.baidu.com,weibo.com,www.baidu.com; SINAGLOBAL=2231131084364.6147.1691322221755; SCF=Agl4_AP0sUSdjP_kMa2XS8k0pgE1RWAjtrfBVaY8k1PouM_Xqv9a7wGYqTn1Gq3nYQQnucccf79-7YJ9kRxdp74.; SUB=_2A25LhsHADeRhGeRG6lYT8SnNyjuIHXVo-lsIrDV8PUNbmtANLW7ikW9NTfOQzxjxFQeVB3IuVZf-r-Vi-Lq8rp5_; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWB-A_3WoZKGd4zMIkHDoTj5JpX5KzhUgL.FozReKBEeKMpeKM2dJLoIXnLxKBLB.BL1K-LxK-LBKBL1hBLxK-LB-qLB.zLxKqL1h.LB.-LxKBLBonL1h5LxKML1h.L1hMLxK-LB--L1h.LxK-LB--L1h2t; ALF=02_1722433168; _s_tentry=-; Apache=5033914820214.327.1719841393049; ULV=1719841393051:5:1:1:5033914820214.327.1719841393049:1708779649720',
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        }
        page = 0
        pageCount = 1

        while True:
            weibo_content = []
            weibo_liketimes = []
            weibo_date = []
            page = page + 1
            tempUrl = url + '&page=' + str(page)
            print('-' * 36, tempUrl, '-' * 36)
            response = requests.get(tempUrl, headers=headers_com)
            html = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
            count = len(html.xpath('//div[@class="card-wrap"]')) - 2
            print('count', count)
            for i in range(1, count + 1):
                try:
                    contents = html.xpath('//div[@class="card-wrap"][' + str(
                        i) + ']/div[@class="card"]/div[1]/div[2]/p[@node-type="feed_list_content_full"]')
                    contents = contents[0].xpath('string(.)').strip()  # 读取该节点下的所有字符串
                except:
                    contents = html.xpath('//div[@class="card-wrap"][' + str(
                        i) + ']/div[@class="card"]/div[1]/div[2]/p[@node-type="feed_list_content"]')
                    # 如果出错就代表当前这条微博有问题
                    try:
                        contents = contents[0].xpath('string(.)').strip()
                    except:
                        continue
                contents = contents.replace('收起全文d', '')
                contents = contents.replace('收起d', '')
                contents = contents.split(' 2')[0]

                add_data = {}

                # 发微博的人的名字
                name = html.xpath(
                    '//div[@class="card-wrap"][' + str(i) + ']/div[@class="card"]/div[1]/div[2]/div[1]/div[2]/a')[
                    0].text
                print('name', name)
                add_data['author_name'] = name
                # 微博url
                weibo_url = html.xpath('//div[@class="card-wrap"][' + str(
                    i) + ']/div[@class="card"]/div[1]/div[2]/div[@class="from"]/a/@href')[0]
                print('weibo_url', weibo_url)
                add_data['blog_url'] = "https:" + weibo_url

                url_str = '.*?com\/\d+\/(.*)\?refer_flag=\d+_'
                res = re.findall(url_str, weibo_url)
                blog_id = res[0]
                print('blog_id', blog_id)
                add_data['blog_id'] = blog_id

                # 获取微博用户ID
                pattern = r"weibo\.com/(\d+)/"
                match = re.search(pattern, weibo_url)
                if match:
                    user_id = match.group(1)
                    print('user_id',user_id)
                    add_data['author_id'] = user_id

                # 发微博的时间
                publish_time = html.xpath('//div[@class="card-wrap"][' + str(
                        i) + ']/div[@class="card"]/div[1]/div[2]/div[@class="from"]/a')[0].text.strip()
                print('publish_time',publish_time)
                add_data['publish_time'] = publish_time

                # 微博内容
                blog_content = html.xpath('//div[@class="card-wrap"][' + str(
                    i) + ']/div[@class="card"]/div[1]/div[2]/p')[0].text.strip()
                print('blog_content',blog_content)
                add_data['blog_content'] = blog_content

                # 点赞数
                like_count = html.xpath(
                    '//div[@class="card-wrap"][' + str(i) + ']/div[@class="card"]/div[2]/ul[1]/li[3]/a/button/span[2]')[
                    0].text
                # 如果点赞数为空，那么代表点赞数为0
                if like_count == '赞':
                    like_count = 0
                print('like_count', like_count)
                add_data['like_count'] = like_count

                add_data['key_word'] = key_word
                add_data['key_word_id'] = key_word_id

                if not BlogInfo.objects.filter(blog_id=blog_id).exists():
                    BlogInfo.objects.create(**add_data)

                print('=' * 66)
            try:
                if pageCount == 1:
                    pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a')[0].text
                    print(pageA)
                    pageCount = pageCount + 1
                elif pageCount == 3:
                    print('没有下一页了')
                    break
                else:
                    pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a[2]')[0].text
                    pageCount = pageCount + 1
                    print(pageA)
            except:
                print('没有下一页了')
                break


    def get_blog_list(self, request):
        data = json.loads(request.body)
        print('data', data)

        page = data.get('pageNum', 1)
        page_size = data.get('pageSize', 10)
        # 获取搜索条件
        key_word_id = data.get('keywords')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        author_name = data.get('author_name')

        # 初始化查询集
        queryset = BlogInfo.objects.all()

        # 根据关键词ID过滤
        if key_word_id is not None:
            queryset = queryset.filter(key_word_id=key_word_id)

        # 根据开始和结束时间过滤
        if start_time and end_time:
            start_datetime = parse_datetime(start_time)
            end_datetime = parse_datetime(end_time)
            if start_datetime and end_datetime and start_datetime <= end_datetime:
                queryset = queryset.filter(Q(c_time__gte=start_datetime) & Q(c_time__lte=end_datetime))
            else:
                # 返回错误信息，提示时间范围不正确
                return api_return_error('时间范围不正确！', 110003)

        # 根据作者名称过滤
        if author_name:
            queryset = queryset.filter(author_name=author_name)

        # 执行查询
        blogInfoList = queryset
        paginator = Paginator(blogInfoList, page_size)

        try:
            blog_info_page = paginator.page(page)
        except PageNotAnInteger:
            blog_info_page = paginator.page(1)
        except EmptyPage:
            blog_info_page = paginator.page(paginator.num_pages)

        data_list = []
        for info in blog_info_page:
            data_list.append({
                'id': info.id,
                'key_word': info.key_word,
                'key_word_id': info.key_word_id,
                'blog_id': info.blog_id,
                'author_name': info.author_name,
                'author_id': info.author_id,
                'blog_url': info.blog_url,
                'like_count': info.like_count,
                'publish_time': info.publish_time,
                'blog_content': info.blog_content,
                'createTime': info.c_time.strftime('%Y-%m-%d %H:%M:%S'),
                'updateTime': info.u_time.strftime('%Y-%m-%d %H:%M:%S'),
            })
        res_data = {
            'total': paginator.count,
            'pageNum': blog_info_page.number,
            'pageSize': page_size,
            'list': data_list
        }

        return api_return_success(res_data)




