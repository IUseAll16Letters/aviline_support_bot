# Generated by Django 4.2 on 2023-10-26 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aviline', '0008_product_is_subproduct_of_delete_subproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_subproduct_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subproduct', to='aviline.product'),
        ),
    ]
