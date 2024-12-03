# Generated by Django 5.1.1 on 2024-11-27 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_system_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_text', models.TextField()),
                ('translated_text', models.TextField()),
                ('word_count', models.IntegerField()),
                ('translated_word_count', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WordDictionary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('english_word', models.CharField(max_length=100)),
                ('russian_word', models.CharField(max_length=100)),
                ('pos_tag', models.CharField(max_length=50)),
                ('frequency', models.IntegerField(default=1)),
                ('grammar_info', models.TextField()),
            ],
            options={
                'ordering': ['-frequency'],
            },
        ),
    ]