# Generated by Django 4.0.4 on 2022-08-05 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0049_alter_userprofile_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='logo',
        ),
    ]