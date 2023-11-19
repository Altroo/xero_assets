from typing import Union

from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AssetSettingSerializer, AssetTypeSerializer, AssetsSerializer
from .models import AssetSetting, AssetType, Asset


class AssetSettingsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        user_pk: int = request.user.pk
        start_date: str = request.data.get('start_date')
        capital_gain_on_disposal: int = request.data.get('capital_gain_on_disposal_pk')
        gain_on_disposal: int = request.data.get('gain_on_disposal_pk')
        loss_on_disposal: int = request.data.get('loss_on_disposal_pk')
        serializer: AssetSettingSerializer = AssetSettingSerializer(data={
            'user': user_pk,
            'start_date': start_date,
            'capital_gain_on_disposal': capital_gain_on_disposal,
            'gain_on_disposal': gain_on_disposal,
            'loss_on_disposal': loss_on_disposal,
        })
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        try:
            asset_setting: Union[QuerySet, AssetSetting] = AssetSetting.objects.get(user=user)
            asset_setting_serializer: AssetSettingSerializer = AssetSettingSerializer(asset_setting)
            return Response(data=asset_setting_serializer.data, status=status.HTTP_200_OK)
        except AssetSetting.DoesNotExist:
            raise NotFound('Asset setting for this user do not exist.')

    @staticmethod
    def patch(request, *args, **kwargs):
        user = request.user
        try:
            asset_setting: Union[QuerySet, AssetSetting] = AssetSetting.objects.get(user=user)
            start_date = request.data.get('start_date')
            if start_date:
                data = {
                    "start_date": request.data.get('start_date'),
                }
            else:
                data = {
                    "capital_gain_on_disposal": request.data.get('capital_gain_on_disposal_pk'),
                    "gain_on_disposal": request.data.get('gain_on_disposal_pk'),
                    "loss_on_disposal": request.data.get('loss_on_disposal_pk'),
                }
            serializer: AssetSettingSerializer = AssetSettingSerializer(asset_setting, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            raise ValidationError(serializer.errors)
        except AssetSetting.DoesNotExist:
            raise NotFound('Asset setting for this user do not exist.')


class AssetTypesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        user_pk: int = request.user.pk
        asset_type: str = request.data.get('asset_type')
        asset_account: int = request.data.get('asset_account_pk')
        accumulated_depreciation_account: int = request.data.get('accumulated_depreciation_account_pk')
        depreciation_expense_account: int = request.data.get('depreciation_expense_account_pk')
        depreciation_method: str = request.data.get('depreciation_method')
        averaging_method: str = request.data.get('averaging_method')
        rate: Union[float, None] = request.data.get('rate')
        effective_life: Union[int, None] = request.data.get('effective_life')
        serializer: AssetTypeSerializer = AssetTypeSerializer(data={
            'user': user_pk,
            'asset_type': asset_type,
            'asset_account': asset_account,
            'accumulated_depreciation_account': accumulated_depreciation_account,
            'depreciation_expense_account': depreciation_expense_account,
            'depreciation_method': depreciation_method,
            'averaging_method': averaging_method,
            'rate': rate,
            'effective_life': effective_life,
        })
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        asset_type_pk: int = kwargs.get('asset_type_pk')
        try:
            asset_type: Union[QuerySet, AssetType] = AssetType.objects.get(pk=asset_type_pk, user=user)
            asset_type_serializer: AssetTypeSerializer = AssetTypeSerializer(asset_type)
            return Response(data=asset_type_serializer.data, status=status.HTTP_200_OK)
        except AssetType.DoesNotExist:
            raise NotFound('Asset type for this user do not exist.')

    @staticmethod
    def patch(request, *args, **kwargs):
        user = request.user
        asset_type_pk: int = request.data.get('asset_type_pk')
        try:
            asset_type_obj: Union[QuerySet, AssetType] = AssetType.objects.get(pk=asset_type_pk, user=user)
            asset_type: str = request.data.get('asset_type')
            asset_account: int = request.data.get('asset_account_pk')
            accumulated_depreciation_account: int = request.data.get('accumulated_depreciation_account_pk')
            depreciation_expense_account: int = request.data.get('depreciation_expense_account_pk')
            depreciation_method: str = request.data.get('depreciation_method')
            averaging_method: str = request.data.get('averaging_method')
            rate: Union[float, None] = request.data.get('rate')
            effective_life: Union[int, None] = request.data.get('effective_life')
            data = {
                "user": user.pk,
                "asset_type": asset_type,
                "asset_account": asset_account,
                "accumulated_depreciation_account": accumulated_depreciation_account,
                "depreciation_expense_account": depreciation_expense_account,
                "depreciation_method": depreciation_method,
                "averaging_method": averaging_method,
                "rate": rate,
                "effective_life": effective_life,
            }
            serializer: AssetTypeSerializer = AssetTypeSerializer(asset_type_obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            raise ValidationError(serializer.errors)
        except AssetType.DoesNotExist:
            raise NotFound('Asset type for this user do not exist.')


class AssetsView(APIView, PageNumberPagination):
    permission_classes = (permissions.IsAuthenticated,)
    page_size = 10

    @staticmethod
    def post(request, *args, **kwargs):
        user_pk: int = request.user.pk
        asset_name: str = request.data.get('asset_name')
        asset_number: str = request.data.get('asset_number')
        purchase_date: str = request.data.get('purchase_date')
        purchase_price: float = request.data.get('purchase_price')
        warranty_expiry: str = request.data.get('warranty_expiry')
        serial_number: str = request.data.get('serial_number')
        asset_type: int = request.data.get('asset_type_pk')
        region: str = request.data.get('region')
        description: str = request.data.get('description')
        depreciation_start_date: str = request.data.get('depreciation_start_date')
        cost_limit: float = request.data.get('cost_limit')
        residual_value: float = request.data.get('residual_value')
        depreciation_method: str = request.data.get('depreciation_method')
        averaging_method: str = request.data.get('averaging_method')
        rate: Union[float, None] = request.data.get('rate')
        effective_life: Union[int, None] = request.data.get('effective_life')
        # Save as draft or register
        asset_status: str = request.data.get('asset_status')
        serializer: AssetsSerializer = AssetsSerializer(data={
            'user': user_pk,
            'asset_name': asset_name,
            'asset_number': asset_number,
            'purchase_date': purchase_date,
            'purchase_price': purchase_price,
            'warranty_expiry': warranty_expiry,
            'serial_number': serial_number,
            'asset_type': asset_type,
            'region': region,
            'description': description,
            'depreciation_start_date': depreciation_start_date,
            'cost_limit': cost_limit,
            'residual_value': residual_value,
            'depreciation_method': depreciation_method,
            'averaging_method': averaging_method,
            'rate': rate,
            'effective_life': effective_life,
            'asset_status': asset_status,
        })
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors)

    def get(self, request, *args, **kwargs):
        user = request.user
        messages = Asset.objects.filter(user=user)
        page = self.paginate_queryset(request=request, queryset=messages)
        if page is not None:
            serializer = AssetsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @staticmethod
    def patch(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        asset_status: str = request.data.get('asset_status')
        asset_pks_list = str(asset_pk).split(',')
        Asset.objects.filter(user=user, pk__in=asset_pks_list).update(asset_status=asset_status)
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        asset_pks_list = str(asset_pk).split(',')
        Asset.objects.filter(user=user, pk__in=asset_pks_list).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
