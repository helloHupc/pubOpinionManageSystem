## 可视化系统API接口代码

> 《基于社交媒体情感分析的品牌声誉舆情管理研究》

------

此项目是论文中舆情管理可视化系统的API接口代码。还包括admin后台管理，超级管理员登录后台进行前台用户和数据管理。

项目基于Django框架进行开发。

#### 运行环境

代码运行在**RTX4060Ti 16G**加**32G**内存的本地环境。因项目中有LLM大模型调用，所以需要GPU环境，大模型需要放到根目录的`save_trained_model`目录下。

项目依赖扩展参见：[requirements.txt](requirements.txt)

#### 项目启动

```bash
# 需要先迁移数据库文件
python manage.py migrate

# 用8000端口启动项目
python manage.py runserver 127.0.0.1:8000
```

