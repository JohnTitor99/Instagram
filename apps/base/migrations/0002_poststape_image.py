# Generated by Django 4.0.4 on 2022-06-12 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poststape',
            name='image',
            field=models.ImageField(null=True, upload_to='image'),
        ),
    ]
