# Generated by Django 4.2.7 on 2023-12-01 02:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixed_assets', '0006_assetaccount_account_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculatedDepreciation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_value', models.FloatField(blank=True, null=True, verbose_name='Book value')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calculated_depreciation_asset', to='fixed_assets.asset', verbose_name='Asset')),
            ],
            options={
                'verbose_name': 'Calculated Depreciation',
                'verbose_name_plural': 'Calculated Depreciations',
            },
        ),
    ]
