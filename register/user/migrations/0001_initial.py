# Generated by Django 4.0.3 on 2022-08-22 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UsersInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=1000)),
                ('age', models.IntegerField(default=0)),
                ('email', models.EmailField(default='', max_length=254)),
                ('badge', models.IntegerField(default=0)),
                ('phone_number', models.IntegerField(default=0)),
                ('register_time', models.DateField(auto_now_add=True, null=True)),
                ('ticket', models.CharField(default='', max_length=1000)),
            ],
        ),
    ]
