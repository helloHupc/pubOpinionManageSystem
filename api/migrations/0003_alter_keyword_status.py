# Generated by Django 5.0.2 on 2024-07-06 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_keyword_options_keyword_u_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]
