# Generated by Django 4.0.4 on 2022-09-29 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0069_alter_reply_related_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='reply',
            options={'ordering': ['-created']},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Prefer not to say', 'Prefer not to say')], max_length=17, null=True),
        ),
    ]