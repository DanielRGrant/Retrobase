# Generated by Django 3.0.4 on 2020-06-02 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dnarecord',
            name='dnaseq',
            field=models.TextField(max_length=1000000),
        ),
    ]