# Generated by Django 3.2 on 2024-08-19 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0002_role_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('branch_id', models.AutoField(primary_key=True, serialize=False)),
                ('branch_name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=255)),
                ('manager', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Branch',
            },
        ),
    ]