# Generated by Django 5.0.2 on 2024-06-29 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_user_avatar_user_roles'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='UserProfile',
        ),
        migrations.RenameField(
            model_name='confirmstring',
            old_name='user',
            new_name='UserProfile',
        ),
    ]