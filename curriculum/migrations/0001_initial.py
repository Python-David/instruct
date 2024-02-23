# Generated by Django 4.2.10 on 2024-02-19 21:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('country', models.CharField(max_length=50)),
                ('education_level', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('curriculum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='curriculum.curriculum')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('week', models.IntegerField()),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='curriculum.subject')),
            ],
        ),
    ]
