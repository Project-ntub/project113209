from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0002_user_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_image',
        ),
    ]