# Generated by Django 2.2 on 2019-04-26 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_auto_20190425_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='phone_number',
            field=models.CharField(blank=True, max_length=128, unique=True),
        ),
    ]
