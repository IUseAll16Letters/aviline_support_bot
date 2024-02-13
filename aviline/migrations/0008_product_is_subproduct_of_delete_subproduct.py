# Generated by Django 4.2 on 2023-10-22 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aviline', '0007_created_product_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_subproduct_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aviline.product'),
        ),
        migrations.DeleteModel(
            name='SubProduct',
        ),
    ]
