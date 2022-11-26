# Generated by Django 4.1.3 on 2022-11-26 16:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bot', '0002_alter_tguser_options_alter_tguser_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tguser',
            name='username',
            field=models.CharField(blank=True, default=None, max_length=255, verbose_name='Username'),
        ),
    ]
