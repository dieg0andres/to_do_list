# Generated by Django 4.2.15 on 2024-09-07 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('to_dos', '0006_profileuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='doitem',
            name='tag',
            field=models.CharField(default='home', max_length=50),
        ),
    ]
