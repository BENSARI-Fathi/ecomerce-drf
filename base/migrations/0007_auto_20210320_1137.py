# Generated by Django 3.1.4 on 2021-03-20 11:37

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20210314_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='./placeholder.png', null=True, upload_to=base.models.upload_update_image),
        ),
    ]
