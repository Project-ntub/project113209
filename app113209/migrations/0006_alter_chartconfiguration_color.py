# Generated by Django 3.2 on 2024-11-13 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0005_chartconfiguration_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartconfiguration',
            name='color',
            field=models.JSONField(default=dict),
        ),
    ]
