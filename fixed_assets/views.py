from calendar import monthrange
from datetime import datetime, date
from typing import Union, Dict

from django.db.models import QuerySet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (AssetSettingSerializer, AssetTypeSerializer, AssetsSerializer, AssetsListSerializer,
                          AssetTypeListSerializer, CalculatedDepreciationSerializer)
from .models import AssetSetting, AssetType, Asset
from .utils import StraightLine, FullDepreciation, DecliningBalanceBy100Or150Or200


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


class AssetTypesView(APIView, PageNumberPagination):
    permission_classes = (permissions.IsAuthenticated,)
    page_size = 10

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

    # @staticmethod
    # def get(request, *args, **kwargs):
    #     user = request.user
    #     asset_type_pk: int = kwargs.get('asset_type_pk')
    #     try:
    #         asset_type: Union[QuerySet, AssetType] = AssetType.objects.get(pk=asset_type_pk, user=user)
    #         asset_type_serializer: AssetTypeSerializer = AssetTypeSerializer(asset_type)
    #         return Response(data=asset_type_serializer.data, status=status.HTTP_200_OK)
    #     except AssetType.DoesNotExist:
    #         raise NotFound('Asset type for this user do not exist.')

    def get(self, request, *args, **kwargs):
        user = request.user
        asset_type_pk: int = kwargs.get('asset_type_pk')
        # Get One Asset Type
        if asset_type_pk:
            try:
                asset_type: Union[QuerySet, AssetType] = AssetType.objects.get(pk=asset_type_pk, user=user)
                asset_type_serializer: AssetTypeListSerializer = AssetTypeListSerializer(asset_type)
                return Response(data=asset_type_serializer.data, status=status.HTTP_200_OK)
            except AssetType.DoesNotExist:
                raise NotFound('Asset type for this user do not exist.')
        # Get list of asset types
        asset_types: Union[QuerySet, AssetType] = AssetType.objects.filter(user=user).order_by('-pk')
        page = self.paginate_queryset(request=request, queryset=asset_types)
        if page is not None:
            serializer: AssetTypeListSerializer = AssetTypeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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


class AssetsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

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
        data = {
            'user': user_pk,
            'asset_name': asset_name,
            'asset_number': asset_number,
            'purchase_date': purchase_date,
            'purchase_price': float(purchase_price) if purchase_price else None,
            'warranty_expiry': warranty_expiry,
            'serial_number': serial_number,
            'asset_type': asset_type,
            'region': region,
            'description': description,
            'depreciation_start_date': depreciation_start_date,
            'cost_limit': float(cost_limit) if cost_limit else None,
            'residual_value': float(residual_value) if residual_value else None,
            'depreciation_method': depreciation_method,
            'averaging_method': averaging_method,
            'rate': float(rate) if rate else None,
            'effective_life': float(effective_life) if effective_life else None,
            'asset_status': asset_status,
        }
        serializer: AssetsSerializer = AssetsSerializer(data=data)
        if serializer.is_valid():
            if depreciation_method == 'ST':
                book_value: Union[float, int] = StraightLine(data).calculate_depreciation()
            elif depreciation_method in ['100', '150', '200']:
                book_value: Union[float, int] = (DecliningBalanceBy100Or150Or200(data)
                                                 .calculate_depreciation())
            elif depreciation_method == 'FD':
                book_value: Union[float, int] = FullDepreciation(data).calculate_depreciation()
            else:
                book_value: Union[float, int] = 0
            # Only if asset is registered
            if asset_status == 'RE':
                new_book_value: float = int(data.get('purchase_price')) - book_value
                date_object: date = datetime.strptime(data.get('depreciation_start_date'), '%Y-%m-%d').date()
                last_month_day: int = monthrange(date_object.year, date_object.month)[1]
                last_date: date = date(date_object.year, date_object.month, last_month_day)
                data: Dict[str, Union[int, str, float, None]] = {
                    **data,
                    'book_value': new_book_value,
                }
                asset = serializer.save()
                calculated_depreciation_serializer: CalculatedDepreciationSerializer = (
                    CalculatedDepreciationSerializer(data={
                        'asset': asset.pk,
                        'depreciation_of': book_value,
                        'depreciation_date': last_date
                    }))
                if calculated_depreciation_serializer.is_valid():
                    calculated_depreciation_serializer.save()
                    return Response(data=data, status=status.HTTP_200_OK)
                raise ValidationError(calculated_depreciation_serializer.errors)
        raise ValidationError(serializer.errors)

    @staticmethod
    def patch(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        asset_status: str = request.data.get('asset_status')
        # Edit only as Registered and Draft
        if asset_status != 'DI':
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


class ListAssetsView(ListAPIView, PageNumberPagination):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AssetsListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['asset_name', 'asset_number', 'purchase_date', 'purchase_price']
    ordering = ['-pk']
    search_fields = ['asset_name', 'asset_number', 'asset_type__asset_type', 'description']
    http_method_names = ('get',)
    page_size = 10

    def get_queryset(self) -> Union[QuerySet, Asset]:
        user = self.request.user
        queryset: QuerySet[Asset] = Asset.objects.filter(user=user)
        return self.get_list_by_asset_status(queryset)

    def get_list_by_asset_status(self, queryset: QuerySet) -> QuerySet:
        asset_status: str = self.request.query_params.get('asset_status', None)
        if asset_status:
            query: QuerySet = queryset.filter(asset_status=asset_status)
            return query
        return Asset.objects.none()

    def list(self, request, *args, **kwargs):
        queryset: Union[QuerySet, Asset] = self.get_queryset()
        filter_queryset: QuerySet = self.filter_queryset(queryset)
        page = self.paginate_queryset(filter_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class AssetNumbersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        assets: Union[QuerySet, Asset] = Asset.objects.filter(user=user)
        registered = assets.filter(asset_status='RE').count()
        draft = assets.filter(asset_status='DR').count()
        disposed = assets.filter(asset_status='DI').count()
        data: Dict[str, int] = {
            'registered': registered,
            'draft': draft,
            'disposed': disposed
        }
        return Response(data=data, status=status.HTTP_200_OK)


class AssetRunDepreciationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        pass
