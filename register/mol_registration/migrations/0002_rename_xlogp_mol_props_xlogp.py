# Generated by Django 4.0.3 on 2022-08-22 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mol_registration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mol_props',
            old_name='XLOGP',
            new_name='xlogp',
        ),
    ]
