# Generated by Django 3.2.15 on 2023-02-16 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20230131_0617'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='User',
            new_name='user',
        ),
    ]