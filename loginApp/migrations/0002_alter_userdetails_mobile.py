# Generated by Django 4.0.6 on 2022-11-15 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdetails',
            name='mobile',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]