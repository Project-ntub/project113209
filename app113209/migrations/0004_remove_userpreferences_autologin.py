
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app113209', '0003_remove_user_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpreferences',
            name='autoLogin',
        ),
    ]