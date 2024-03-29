# Generated by Django 4.2 on 2023-09-12 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aviline', '0001_created_models_product_prod_problem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.PositiveBigIntegerField()),
                ('question', models.TextField()),
                ('is_solved', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TicketMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('telegram_id', models.PositiveBigIntegerField()),
                ('media_type', models.IntegerField()),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aviline.ticket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
