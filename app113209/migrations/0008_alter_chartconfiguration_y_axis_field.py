# Generated by Django 3.2 on 2024-11-22 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0007_merge_20241120_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartconfiguration',
            name='y_axis_field',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
