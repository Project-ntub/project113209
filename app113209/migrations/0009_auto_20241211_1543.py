# Generated by Django 3.2 on 2024-12-11 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0008_alter_chartconfiguration_y_axis_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendarevent',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='calendarevent',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='color',
            field=models.CharField(default='blue', max_length=50),
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='privacy',
            field=models.CharField(choices=[('public', '公開'), ('private', '私人')], default='public', max_length=10),
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='user',
            field=models.ForeignKey(default=36, on_delete=django.db.models.deletion.CASCADE, to='app113209.user'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='UserLayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layout', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_layouts',
            },
        ),
    ]