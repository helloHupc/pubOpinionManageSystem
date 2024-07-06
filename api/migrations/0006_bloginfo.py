# Generated by Django 5.0.2 on 2024-07-06 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_rename_user_id_keyword_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blog_id', models.CharField(max_length=256)),
                ('author_name', models.CharField(max_length=256)),
                ('author_id', models.CharField(max_length=256)),
                ('publish_time', models.CharField(max_length=256)),
                ('blog_content', models.TextField(blank=True, null=True)),
                ('type', models.CharField(default='weibo', max_length=30)),
                ('c_time', models.DateTimeField(auto_now_add=True)),
                ('u_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '微博博文',
                'verbose_name_plural': '微博博文',
                'ordering': ['-c_time', '-u_time'],
            },
        ),
    ]
