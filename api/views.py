import uuid
import json
from django.views import View
from login.models import UserProfile
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.utils import encrypt_user_id, api_return_error, api_return_success
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.db import models
from django.utils.dateparse import parse_datetime
from api.models import KeyWord, BlogInfo, DynamicDataset
import requests
from lxml import etree
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
from tqdm import tqdm
import os
from django.utils import timezone
from datetime import timedelta, datetime
import csv
import io
from django.http import HttpResponse


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
            {
                'path': "/dynamic-dataset",
                'component': "Layout",
                'name': "DynamicDataset",
                'redirect': "/dynamic-dataset/page",
                'meta': {
                    'title': "动态数据集管理",
                    'icon': "document",
                    'hidden': False,
                    'roles': ["ADMIN"],
                },
                'children': [
                    {
                        'path': "page",
                        'component': "dynamic-dataset/page",
                        'name': "DynamicDatasetPage",
                        'meta': {
                            'title': "动态数据集管理",
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
        print('data', data)

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
            'Cookie': 'SINAGLOBAL=7156742576788.246.1720268063899; SCF=Al7ljahTPnneEMetgfZh8wLJaooFa1luU6A7LmDJAKc5aK-mjaCWhQpzS9FHus902kWVctpQg8ObDyBoQdStsGw.; SUB=_2A25L88dQDeRhGeRG6lYT8SnNyjuIHXVpcUaYrDV8PUNbmtANLUjhkW9NTfOQzyJ9u6PL1KSLG6PtKZFjFTBAqVS5; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWB-A_3WoZKGd4zMIkHDoTj5JpX5KzhUgL.FozReKBEeKMpeKM2dJLoIXnLxKBLB.BL1K-LxK-LBKBL1hBLxK-LB-qLB.zLxKqL1h.LB.-LxKBLBonL1h5LxKML1h.L1hMLxK-LB--L1h.LxK-LB--L1h2t; ALF=02_1730102272; _s_tentry=passport.weibo.com; Apache=5945913879617.597.1727510274582; ULV=1727510274632:7:1:1:5945913879617.597.1727510274582:1723287009691',
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
                    print('user_id', user_id)
                    add_data['author_id'] = user_id

                # 发微博的时间
                publish_time = html.xpath('//div[@class="card-wrap"][' + str(
                    i) + ']/div[@class="card"]/div[1]/div[2]/div[@class="from"]/a')[0].text.strip()
                print('publish_time', publish_time)
                add_data['publish_time'] = publish_time

                # 微博内容
                # blog_content = html.xpath('//div[@class="card-wrap"][' + str(
                #     i) + ']/div[@class="card"]/div[1]/div[2]/p')[0].text.strip()
                blog_content = ''.join(html.xpath(
                    '//div[@class="card-wrap"][' + str(i) + ']/div[@class="card"]/div[1]/div[2]/p/text()')).strip()

                print('blog_content', blog_content)
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

                check_exist = BlogInfo.objects.filter(blog_id=blog_id).exists()

                if not check_exist and add_data.get('blog_content') and len(blog_content) > 3:
                    BlogInfo.objects.create(**add_data)

                print('=' * 66)
            try:
                if pageCount == 1:
                    pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a')[0].text
                    print(pageA)
                    pageCount = pageCount + 1
                elif pageCount == 50:
                    print('抓取完 没有下一页了')
                    break
                else:
                    pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a[2]')[0].text
                    pageCount = pageCount + 1
                    print(pageA)
            except:
                print('except 没有下一页了')
                break

    def get_blog_list(self, request):
        data = json.loads(request.body)
        print('data', data)

        page = data.get('pageNum', 1)
        page_size = data.get('pageSize', 10)
        # 获取搜索条件
        key_word_id = data.get('keywords')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
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
        need_llm = False
        for item in blog_info_page:
            if item.sentiment is None or item.sentiment.strip() == '':
                need_llm = True
                break

        if need_llm:
            model, tokenizer = self.init_llm_model()

        for info in blog_info_page:
            print('info.sentiment', info.sentiment)
            print('info.blog_content', info.blog_content)
            blog_sentiment = info.sentiment
            if need_llm and info.blog_content is not None:
                blog_sentiment = self.analyze_sentiment(info.blog_content, model, tokenizer)

                # 将sentiment写入数据库中
                blog_obj = BlogInfo.objects.get(id=info.id)
                blog_obj.sentiment = data.get('sentiment', blog_sentiment)
                # 保存对象
                blog_obj.save()

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
                'is_add_dynamic_dataset': info.is_add_dynamic_dataset,
                'blog_sentiment': blog_sentiment,
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

    # 初始化模型
    def init_llm_model(self):
        # 定义保存模型的文件夹路径
        save_trained_folder = "./save_trained_model/WeiboSentiment-Qwen2-1.5B-Instruct"

        # 加载本地微调好的模型和分词器
        print('save_trained_folder', save_trained_folder)
        # 检查路径是否存在，如果不存在则创建
        if not os.path.exists(save_trained_folder):
            print('save_trained_folder not exists')

        print('gpu is_available', torch.cuda.is_available())

        model = AutoModelForCausalLM.from_pretrained(save_trained_folder)
        tokenizer = AutoTokenizer.from_pretrained(save_trained_folder)

        # 移动模型到GPU（如果可用）
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        return model, tokenizer

    # 调用llm预测微博博文情感
    def analyze_sentiment(self, sentence, model, tokenizer):

        # 将句子转化为 DataFrame
        sentence_df = pd.DataFrame({"text": [sentence]})

        # 应用 generate_test_prompt 函数格式化句子
        formatted_sentence = sentence_df.apply(self.generate_test_prompt, axis=1)

        # 将格式化后的句子转化为 DataFrame，模拟 x_test 的格式
        formatted_sentence_df = pd.DataFrame(formatted_sentence, columns=["text"])

        # 使用加载的模型进行预测
        predictions = self.predict(formatted_sentence_df, model, tokenizer)
        print("Predictions:", predictions)
        return predictions

    # 定义预测函数
    def predict(self, test_data, model, tokenizer):
        y_pred = []
        for i in tqdm(range(len(test_data))):
            prompt = test_data.iloc[i]["text"]
            input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
            outputs = model.generate(**input_ids, max_new_tokens=1, temperature=0.001, do_sample=True)
            result = tokenizer.decode(outputs[0])
            answer = result.split("=")[-1].lower()
            if "positive" in answer:
                return "positive"
            elif "negative" in answer:
                return "negative"
            else:
                return "none"

    def generate_test_prompt(self, data_point):
        return f"""
                Analyze the sentiment of the text enclosed in square brackets, 
                determine if it is positive, or negative, and return the answer as 
                the corresponding sentiment label "positive" or "negative"

                [{data_point["text"]}] = 

                """.strip()


class DashboardView(View):
    def post(self, request, action):
        if action == 'get_card_info':
            # 首页卡片信息
            return self.get_card_info(request)
        elif action == 'get_recent_blog_num':
            # 获取最近7天微博数量
            return self.get_recent_blog_num(request)
        elif action == 'get_blog_num_group_by_keyword':
            # 以关键词分组获取微博数量
            return self.get_blog_num_group_by_keyword(request)
        else:
            return api_return_error('请求错误！', 120001)

    def get_card_info(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # 获取当天的总数量
        today_total = BlogInfo.objects.filter(c_time__date=today).count()

        # 获取前一天的总数量
        yesterday_total = BlogInfo.objects.filter(c_time__date=yesterday).count()

        # 计算总数量的增长率
        if yesterday_total > 0:
            total_growth_rate = ((today_total - yesterday_total) / yesterday_total) * 100
        else:
            total_growth_rate = 0

        # 获取当天 sentiment 为 positive 的数量
        today_positive = BlogInfo.objects.filter(c_time__date=today, sentiment='positive').count()

        # 获取前一天 sentiment 为 positive 的数量
        yesterday_positive = BlogInfo.objects.filter(c_time__date=yesterday, sentiment='positive').count()

        # 计算 positive 数量的增长率
        if yesterday_positive > 0:
            positive_growth_rate = ((today_positive - yesterday_positive) / yesterday_positive) * 100
        else:
            positive_growth_rate = 0

        # 获取当天 sentiment 为 negative 的数量
        today_negative = BlogInfo.objects.filter(c_time__date=today, sentiment='negative').count()

        # 获取前一天 sentiment 为 negative 的数量
        yesterday_negative = BlogInfo.objects.filter(c_time__date=yesterday, sentiment='negative').count()

        # 计算 negative 数量的增长率
        if yesterday_negative > 0:
            negative_growth_rate = ((today_negative - yesterday_negative) / yesterday_negative) * 100
        else:
            negative_growth_rate = 0

        # 获取当前总数量
        total_count_key_word = KeyWord.objects.count()

        # 获取今天的数量
        today_count_key_word = KeyWord.objects.filter(c_time__date=today).count()

        # 计算昨天的数量
        if today_count_key_word > 0:
            yesterday_count_key_word = total_count_key_word - today_count_key_word
            key_word_growth_rate = ((total_count_key_word - yesterday_count_key_word) / yesterday_count_key_word) * 100
        else:
            yesterday_count_key_word = total_count_key_word
            key_word_growth_rate = 0

        res_data = [
            {
                'type': "ip",
                'title': "关键词",
                'todayCount': total_count_key_word,
                'yesterdayCount': yesterday_count_key_word,
                'growthRate': key_word_growth_rate,
                'granularityLabel': "日",
            },
            {
                'type': "ip",
                'title': "微博数量",
                'todayCount': today_total,
                'yesterdayCount': yesterday_total,
                'growthRate': total_growth_rate,
                'granularityLabel': "日",
            },
            {
                'type': "ip",
                'title': "正向微博数量",
                'todayCount': today_positive,
                'yesterdayCount': yesterday_positive,
                'growthRate': positive_growth_rate,
                'granularityLabel': "日",
            },
            {
                'type': "ip",
                'title': "负向微博数量",
                'todayCount': today_negative,
                'yesterdayCount': yesterday_negative,
                'growthRate': negative_growth_rate,
                'granularityLabel': "日",
            },
        ]

        print(res_data)
        return api_return_success(res_data)

    def get_recent_blog_num(self, request):
        # 获取当前时间
        now = timezone.now()
        # 计算7天前的日期
        seven_days_ago = now - timedelta(days=7)

        # 查询最近7天创建的数据，并按日期分组
        queryset = BlogInfo.objects.filter(c_time__gte=seven_days_ago) \
            .annotate(date=Trunc('c_time', 'day')) \
            .values('date') \
            .annotate(count=Count('id')) \
            .order_by('date')

        # 输出结果
        x_list = []
        y_list = []
        for item in queryset:
            # 将 datetime 对象格式化为仅包含日期的字符串
            date_str = item['date'].strftime("%Y-%m-%d")
            x_list.append(date_str)
            y_list.append(item['count'])

        res_data = {
            'x_list': x_list,
            'y_list': y_list,
        }

        return api_return_success(res_data)

    def get_blog_num_group_by_keyword(self, request):
        top_eight_keywords = BlogInfo.objects.exclude(key_word__in=['', None]).values('key_word').annotate(
            count=Count('id')).order_by('-count')[:8]

        res_data = []
        for keyword_count in top_eight_keywords:
            print(f"Keyword: {keyword_count['key_word']}, Count: {keyword_count['count']}")
            item = {
                'value': keyword_count['count'],
                'name': keyword_count['key_word'],
            }
            res_data.append(item)

        return api_return_success(res_data)


class BlogInfoView(View):
    def post(self, request, action):
        if action == 'update_senti':
            # 更新微博的情感
            return self.update_senti(request)
        elif action == 'insert_to_dynamic_dataset':
            # 将微博移动到动态微调数据集
            return self.insert_to_dynamic_dataset(request)
        elif action == 'get_dynamic_dataset_list':
            # 获取动态微调数据集
            return self.get_dynamic_dataset_list(request)
        elif action == 'export_dynamic_dataset_csv':
            # 导出动态微调数据集
            return self.export_dynamic_dataset_csv(request)
        else:
            return api_return_error('请求错误！', 130001)



    def update_senti(self, request):
        data = json.loads(request.body)
        print('update_senti data', data)

        id = data.get('id')
        senti = data.get('senti')
        if id is None or senti is None:
            return api_return_error('数据异常！', 130002)

        blog_obj = BlogInfo.objects.get(id=id)
        blog_obj.sentiment = data.get('sentiment', senti)
        # 保存对象
        blog_obj.save()

        return api_return_success({})

    def insert_to_dynamic_dataset(self, request):
        data = json.loads(request.body)
        print('move_to_dynamic_dataset', data)

        ids = data.get('ids')
        if ids is None:
            return api_return_error('数据异常！', 130002)

        ids_list = ids.split(',')
        for data_id in ids_list:
            print('data_id', data_id)
            blog_obj = BlogInfo.objects.get(id=data_id)

            add_data = {}
            add_data['blog_id'] = blog_obj.blog_id
            add_data['key_word'] = blog_obj.key_word
            add_data['blog_content'] = blog_obj.blog_content
            add_data['sentiment'] = blog_obj.sentiment
            add_data['type'] = blog_obj.type

            check_exist = DynamicDataset.objects.filter(blog_id=blog_obj.blog_id).exists()

            # 写入动态数据集
            if check_exist:
                return api_return_error('数据已存在！', 130003)

            DynamicDataset.objects.create(**add_data)

            # 更新微博数据表状态
            blog_obj.is_add_dynamic_dataset = 1
            # 保存对象
            blog_obj.save()

        return api_return_success({})

    def get_dynamic_dataset_list(self, request):
        data = json.loads(request.body)
        print('data', data)

        page = data.get('pageNum', 1)
        page_size = data.get('pageSize', 10)
        # 获取搜索条件
        start_time = data.get('startTime')
        end_time = data.get('endTime')

        # 初始化查询集
        queryset = DynamicDataset.objects.all()

        # 根据开始和结束时间过滤
        if start_time and end_time:
            start_datetime = parse_datetime(start_time)
            end_datetime = parse_datetime(end_time)
            if start_datetime and end_datetime and start_datetime <= end_datetime:
                queryset = queryset.filter(Q(c_time__gte=start_datetime) & Q(c_time__lte=end_datetime))
            else:
                # 返回错误信息，提示时间范围不正确
                return api_return_error('时间范围不正确！', 110003)

        # 执行查询
        dynamicDatasetList = queryset
        paginator = Paginator(dynamicDatasetList, page_size)

        try:
            dynamic_dataset_page = paginator.page(page)
        except PageNotAnInteger:
            dynamic_dataset_page = paginator.page(1)
        except EmptyPage:
            dynamic_dataset_page = paginator.page(paginator.num_pages)

        data_list = []
        for info in dynamic_dataset_page:
            print('dynamic_dataset.sentiment', info.sentiment)
            print('dynamic_dataset.blog_content', info.blog_content)

            data_list.append({
                'id': info.id,
                'key_word': info.key_word,
                'blog_id': info.blog_id,
                'blog_content': info.blog_content,
                'blog_sentiment': info.sentiment,
                'is_use': info.is_use,
                'createTime': info.c_time.strftime('%Y-%m-%d %H:%M:%S'),
                'updateTime': info.u_time.strftime('%Y-%m-%d %H:%M:%S'),
            })
        res_data = {
            'total': paginator.count,
            'pageNum': dynamic_dataset_page.number,
            'pageSize': page_size,
            'list': data_list
        }

        return api_return_success(res_data)

    def export_dynamic_dataset_csv(self, request):
        data = json.loads(request.body)
        print('export_dynamic_dataset_csv data', data)

        ids = data.get('ids')
        if ids is None:
            return api_return_error('数据异常！', 130002)

        data_list = []

        ids_list = ids.split(',')
        for data_id in ids_list:
            print('data_id', data_id)
            info = DynamicDataset.objects.get(id=data_id)

            data_list.append({
                'sentiment': info.sentiment,
                'blog_content': info.blog_content,
            })

            # 更新数据表状态
            info.is_use = 1
            # 保存对象
            info.save()

        # 获取当前时间并格式化为 YYYYMMDD_HHMMSS 形式
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f'blogsentiment{timestamp}.csv'

        # 使用 io.StringIO 创建一个内存中的文件对象
        output = io.StringIO()

        # 创建 CSV writer，只写 sentiment 和 blog_content 字段
        writer = csv.DictWriter(output, fieldnames=['sentiment', 'blog_content'])
        writer.writeheader()

        # 将 data_list 写入 CSV
        for row in data_list:
            writer.writerow(row)

        # 将内容写入 HttpResponse
        response = HttpResponse(content_type='text/csv;charset=utf-8')

        # 使用 utf-8 编码返回 CSV 内容
        response.write(output.getvalue().encode('utf-8').decode('utf-8'))
        response['Content-Disposition'] = f'attachment;filename={file_name}'

        return response
