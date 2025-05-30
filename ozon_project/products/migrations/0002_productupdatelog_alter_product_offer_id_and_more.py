# Generated by Django 5.2 on 2025-04-14 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductUpdateLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('products_updated', models.IntegerField(default=0)),
            ],
            options={
                'get_latest_by': 'updated_at',
            },
        ),
        migrations.AlterField(
            model_name='product',
            name='offer_id',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_id',
            field=models.IntegerField(db_index=True, unique=True),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['offer_id'], name='products_pr_offer_i_f5f183_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['product_id'], name='products_pr_product_9f5899_idx'),
        ),
    ]
