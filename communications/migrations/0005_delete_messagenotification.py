# Generated by Django 3.0.5 on 2020-08-26 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0004_auto_20200821_1726'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MessageNotification',
        ),
    ]