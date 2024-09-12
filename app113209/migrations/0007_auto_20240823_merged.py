# app113209\migrations\0007_auto_20240823_merged.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0006_datamodel'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='UserPreference',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('fontsize', models.CharField(default='medium', max_length=10)),
        #         ('notificationSettings', models.BooleanField(default=True)),
        #         ('autoLogin', models.BooleanField(default=False)),
        #         ('authentication', models.BooleanField(default=True)),
        #         ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
        #     ],
        #     options={
        #         'db_table': 'userpreferences',
        #     },
        # ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=500)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('device_brand', models.CharField(blank=True, max_length=255, null=True)),
                ('device_type', models.CharField(blank=True, max_length=255, null=True)),
                ('operation_result', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='histories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_history',
            },
        ),
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('chart_type', models.CharField(choices=[('bar', 'Bar Chart'), ('line', 'Line Chart'), ('pie', 'Pie Chart')], max_length=50)),
                ('chart_name', models.CharField(max_length=255)),
                ('chart_data', models.JSONField()),
                ('available', models.BooleanField(default=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('modify_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default='Default Chart Name', max_length=255)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app113209.branch')),
                ('create_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_charts', to=settings.AUTH_USER_MODEL)),
                ('modify_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_charts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'charts',
            },
        ),
        migrations.AddIndex(
            model_name='userhistory',
            index=models.Index(fields=['user'], name='user_histor_user_id_d236a7_idx'),
        ),
        migrations.AddIndex(
            model_name='userhistory',
            index=models.Index(fields=['timestamp'], name='user_histor_timesta_7f64a6_idx'),
        ),
    ]
