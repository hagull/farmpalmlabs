# Generated by Django 2.0.7 on 2019-01-09 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('palm', '0004_auto_20190108_0512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlopengroup',
            name='og_ot',
        ),
        migrations.RemoveField(
            model_name='controlopengroup',
            name='og_tot',
        ),
        migrations.AddField(
            model_name='controletcoption',
            name='ea_op_mode',
            field=models.CharField(choices=[('01', '자동'), ('02', '수동')], default='01', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlfmotoroption',
            name='fm_op_mode',
            field=models.CharField(choices=[('01', '자동'), ('02', '수동')], default='01', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_lm_option',
            field=models.CharField(default='0', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_lm_ot',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_lm_state',
            field=models.CharField(default='0', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_lm_tot',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_rm_option',
            field=models.CharField(default='0', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_rm_ot',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_rm_state',
            field=models.CharField(default='0', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlopengroup',
            name='og_rm_tot',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='controlvmotoroption',
            name='vm_op_mode',
            field=models.CharField(choices=[('01', '자동'), ('02', '수동')], default='01', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='co2_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='co2_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='culture_medium_temp_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='culture_medium_temp_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='humd_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='humd_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='nutrient_solution_ec_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='nutrient_solution_ec_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='nutrient_solution_ph_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='nutrient_solution_ph_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='soil_ec_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='soil_ec_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='soil_humd_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='soil_humd_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='soil_temp_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='soil_temp_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='temp_mean',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensorinfoorvalue',
            name='temp_num',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
