# Generated by Django 4.0.4 on 2022-06-16 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_poststape_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poststape',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/images'),
        ),
    ]
