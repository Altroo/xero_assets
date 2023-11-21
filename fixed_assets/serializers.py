from rest_framework import serializers
from .models import AssetSetting, AssetType, Asset, AssetAccount


class AssetSettingSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(format='%d/%m/%Y')

    class Meta:
        model = AssetSetting
        fields = ['user', 'start_date',
                  'capital_gain_on_disposal',
                  'gain_on_disposal',
                  'loss_on_disposal']
        extra_kwargs = {
            'user': {'write_only': True},
        }


class AssetTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetType
        fields = ['pk', 'user', 'asset_type', 'asset_account',
                  'accumulated_depreciation_account',
                  'depreciation_expense_account',
                  'depreciation_method',
                  'averaging_method',
                  'rate', 'effective_life']
        extra_kwargs = {
            'pk': {'read_only': True},
            'user': {'write_only': True},
            'rate': {'required': False},
            'effective_life': {'required': False},
        }


class AssetTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAccount
        fields = ['pk', 'account_name', 'account_type_code']


class AssetTypeListSerializer(serializers.ModelSerializer):
    asset_account = AssetTypeDetailsSerializer(read_only=True)
    accumulated_depreciation_account = AssetTypeDetailsSerializer(read_only=True)
    depreciation_expense_account = AssetTypeDetailsSerializer(read_only=True)

    class Meta:
        model = AssetType
        fields = ['pk', 'user', 'asset_type', 'asset_account',
                  'accumulated_depreciation_account',
                  'depreciation_expense_account',
                  'depreciation_method',
                  'averaging_method',
                  'rate', 'effective_life']
        extra_kwargs = {
            'user': {'write_only': True},
            'rate': {'required': False},
            'effective_life': {'required': False},
        }


class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['pk', 'user', 'asset_name', 'asset_number',
                  'purchase_date', 'purchase_price',
                  'warranty_expiry', 'serial_number',
                  'asset_type', 'region', 'description',
                  'depreciation_start_date', 'cost_limit',
                  'residual_value', 'depreciation_method',
                  'averaging_method', 'rate', 'effective_life',
                  'asset_status']
        extra_kwargs = {
            'pk': {'read_only': True},
            'user': {'write_only': True},
            'warranty_expiry': {'required': False},
            'serial_number': {'required': False},
            'depreciation_start_date': {'required': False},
            'rate': {'required': False},
            'effective_life': {'required': False},
        }
