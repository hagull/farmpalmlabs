# Generated by Django 2.0.7 on 2019-01-15 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('palm', '0013_testmodel_display_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sensorinfoorvalue',
            old_name='test_date',
            new_name='display_date',
        ),
        migrations.RenameField(
            model_name='weatherinfo',
            old_name='test_date',
            new_name='display_date',
        ),
    ]
