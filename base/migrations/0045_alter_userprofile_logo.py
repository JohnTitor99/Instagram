# Generated by Django 4.0.4 on 2022-07-30 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0044_userprofile_similar_account_suggestions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='logo',
            field=models.ImageField(blank=True, default='media/logo/empty_photo.png', null=True, upload_to='media/logo'),
        ),
    ]