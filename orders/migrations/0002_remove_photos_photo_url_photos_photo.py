# Generated by Django 4.0.6 on 2022-08-20 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photos',
            name='photo_url',
        ),
        migrations.AddField(
            model_name='photos',
            name='photo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
