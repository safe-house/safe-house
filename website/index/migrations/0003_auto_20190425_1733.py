# Generated by Django 2.2 on 2019-04-25 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20190425_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='phone_number',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
