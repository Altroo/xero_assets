from typing import Union

from django.db.models import Sum, QuerySet
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import (AssetSetting, AssetType, Asset, AssetAccount,
                     CalculatedDepreciation, DisposedAsset)
from datetime import datetime, date


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
        fields = ['pk', 'account_name', 'account_type_code', 'account_value']


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


# class AssetsValuesSerializer(serializers.Serializer):
#     purchase_date = serializers.DateField()
#
#     def update(self, instance, validated_data):
#         pass
#
#     def create(self, validated_data):
#         pass


class AssetTypeGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ['pk', 'asset_type']


class AssetsGetSerializer(serializers.ModelSerializer):
    asset_type = AssetTypeGetSerializer(read_only=True)
    basis = SerializerMethodField()
    cost_basis = SerializerMethodField()
    basis_value = SerializerMethodField()
    accumulated_depreciation = SerializerMethodField()
    ytd_depreciation = SerializerMethodField()
    depreciated_to = SerializerMethodField()

    @staticmethod
    def get_ytd_depreciation(obj):
        starting_day_of_current_year: date = datetime.now().date().replace(month=1, day=1)
        result: QuerySet[CalculatedDepreciation] = (CalculatedDepreciation.objects.filter(asset=obj.pk)
                                                    .filter(depreciation_date__gte=starting_day_of_current_year,
                                                            depreciation_date__lte=datetime.now().date()))
        total: Union[float, int] = 0
        i: Union[QuerySet, CalculatedDepreciation]
        for i in result:
            total += i.depreciation_of
        return total

    @staticmethod
    def get_depreciated_to(obj):
        return CalculatedDepreciation.objects.filter(asset=obj.pk).latest('depreciation_date').depreciation_date

    @staticmethod
    def get_accumulated_depreciation(obj):
        return ((CalculatedDepreciation.objects.filter(asset=obj.pk).aggregate(Sum('depreciation_of')))
                .get('depreciation_of__sum'))

    @staticmethod
    def get_basis_value(obj):
        return (int(obj.purchase_price) - (CalculatedDepreciation.objects.filter(asset=obj.pk)
                                           .aggregate(Sum('depreciation_of'))).get('depreciation_of__sum'))

    @staticmethod
    def get_cost_basis(obj):
        return obj.purchase_price

    @staticmethod
    def get_basis(obj):
        return 'Book'

    class Meta:
        model = Asset
        fields = ['pk', 'asset_name', 'asset_number',
                  'purchase_date', 'purchase_price',
                  'warranty_expiry', 'serial_number',
                  'asset_type', 'region', 'description',
                  'depreciation_start_date', 'cost_limit',
                  'residual_value', 'depreciation_method',
                  'averaging_method', 'rate', 'effective_life',
                  'asset_status', 'basis', 'cost_basis', 'basis_value',
                  'accumulated_depreciation', 'ytd_depreciation', 'depreciated_to']


class AssetsListSerializer(serializers.ModelSerializer):
    # book_value = serializers.SerializerMethodField()
    #
    # @staticmethod
    # def get_book_value(instance):
    #     if instance.asset_status == 'RE':
    #         result = CalculatedDepreciation.objects.filter(asset=instance.pk)
    #         purchase_price = float(instance.purchase_price)
    #         for i in result:
    #             purchase_price -= i.depreciation_of
    #         return purchase_price
    #     return instance.purchase_price

    class Meta:
        model = Asset
        fields = ['pk', 'user', 'asset_name', 'asset_number',
                  'purchase_date', 'purchase_price',
                  'warranty_expiry', 'serial_number',
                  'asset_type', 'region', 'description',
                  'depreciation_start_date', 'cost_limit',
                  'residual_value', 'depreciation_method',
                  'averaging_method', 'rate', 'effective_life',
                  'asset_status', 'book_value']
        extra_kwargs = {
            'pk': {'read_only': True},
            'user': {'write_only': True},
            'warranty_expiry': {'required': False},
            'serial_number': {'required': False},
            'depreciation_start_date': {'required': False},
            'rate': {'required': False},
            'effective_life': {'required': False},
        }


class CalculatedDepreciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatedDepreciation
        fields = ['pk', 'asset', 'depreciation_of', 'depreciation_date']
        extra_kwargs = {
            'pk': {'read_only': True},
        }


class DisposedAssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisposedAsset
        fields = ['pk', 'asset', 'disposal_date', 'disposal_price', 'gain_on_disposal_account',
                  'capital_gain_account', 'loss_on_disposal_account', 'gain_losses']
        extra_kwargs = {
            'pk': {'read_only': True},
        }


class AssetsDisposedListSerializer(serializers.ModelSerializer):
    asset_name = serializers.SerializerMethodField()
    asset_number = serializers.SerializerMethodField()
    asset_type = serializers.SerializerMethodField()
    purchase_date = serializers.SerializerMethodField()
    purchase_price = serializers.SerializerMethodField()

    @staticmethod
    def get_asset_name(instance):
        return instance.asset.asset_name

    @staticmethod
    def get_asset_number(instance):
        return instance.asset.asset_number

    @staticmethod
    def get_asset_type(instance):
        return instance.asset.asset_type.asset_type

    @staticmethod
    def get_purchase_date(instance):
        return instance.asset.purchase_date

    @staticmethod
    def get_purchase_price(instance):
        return instance.asset.purchase_price

    class Meta:
        model = DisposedAsset
        fields = ['pk', 'asset_name', 'asset_number',
                  'asset_type', 'purchase_date', 'purchase_price',
                  'disposal_date', 'disposal_price',
                  'gain_losses']
        extra_kwargs = {
            'pk': {'read_only': True},
        }