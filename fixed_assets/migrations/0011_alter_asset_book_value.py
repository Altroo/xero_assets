# Generated by Django 4.2.7 on 2023-12-04 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixed_assets', '0010_asset_book_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='book_value',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Book value'),
        ),
    ]
