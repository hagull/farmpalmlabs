# Generated by Django 2.0.7 on 2019-01-07 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('palm', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testmodel',
            old_name='date1',
            new_name='date',
        ),
    ]
