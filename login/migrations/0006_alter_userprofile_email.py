# Generated by Django 5.0.2 on 2024-06-29 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_alter_userprofile_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(max_length=32),
        ),
    ]
