# Generated by Django 5.0.2 on 2024-07-06 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_keyword_u_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='keyword',
            old_name='user_id',
            new_name='user',
        ),
    ]
