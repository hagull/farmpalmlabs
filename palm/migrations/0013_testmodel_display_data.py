# Generated by Django 2.0.7 on 2019-01-13 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('palm', '0012_auto_20190113_0620'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='display_data',
            field=models.BooleanField(default=False),
        ),
    ]
