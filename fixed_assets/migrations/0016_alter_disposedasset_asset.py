# Generated by Django 4.2.8 on 2023-12-21 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixed_assets', '0015_alter_disposedasset_capital_gain_account_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disposedasset',
            name='asset',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='disposed_asset_asset', to='fixed_assets.asset', verbose_name='Asset'),
        ),
    ]
