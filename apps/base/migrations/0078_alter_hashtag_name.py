# Generated by Django 4.0.4 on 2022-10-05 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0077_remove_hashtag_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
