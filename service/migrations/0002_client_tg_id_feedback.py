# Generated by Django 4.2.1 on 2023-05-29 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='tg_id',
            field=models.IntegerField(default=None, null=True, unique=True, verbose_name='Telegram ID'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_text', models.TextField(verbose_name='Текст обратной связи')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='service.appointment', verbose_name='Посещение')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='service.client', verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Обратная связь',
                'verbose_name_plural': 'Отзывы',
            },
        ),
    ]