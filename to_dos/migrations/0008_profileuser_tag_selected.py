# Generated by Django 4.2.15 on 2024-09-07 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('to_dos', '0007_doitem_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileuser',
            name='tag_selected',
            field=models.CharField(default='home', max_length=50),
        ),
    ]
