from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Union, Dict
from collections import OrderedDict
from cffi.backend_ctypes import xrange

from django.db.models import QuerySet, Sum
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (AssetSettingSerializer, AssetTypeSerializer, AssetsSerializer, AssetsListSerializer,
                          AssetTypeListSerializer, CalculatedDepreciationSerializer,
                          AssetsGetSerializer, DisposedAssetsSerializer, AssetsDisposedListSerializer)
from .models import AssetSetting, AssetType, Asset, CalculatedDepreciation, DisposedAsset
from .utils import StraightLine, FullDepreciation, DecliningBalanceBy100Or150Or200, DisposeAsset2


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

    # @staticmethod
    # def post(request, *args, **kwargs):
    #     user_pk: int = request.user.pk
    #     asset_name: str = request.data.get('asset_name')
    #     asset_number: str = request.data.get('asset_number')
    #     purchase_date: str = request.data.get('purchase_date')
    #     purchase_price: float = request.data.get('purchase_price')
    #     warranty_expiry: str = request.data.get('warranty_expiry')
    #     serial_number: str = request.data.get('serial_number')
    #     asset_type: int = request.data.get('asset_type_pk')
    #     region: str = request.data.get('region')
    #     description: str = request.data.get('description')
    #     depreciation_start_date: str = request.data.get('depreciation_start_date')
    #     cost_limit: float = request.data.get('cost_limit')
    #     residual_value: float = request.data.get('residual_value')
    #     depreciation_method: str = request.data.get('depreciation_method')
    #     averaging_method: str = request.data.get('averaging_method')
    #     rate: Union[float, None] = request.data.get('rate')
    #     effective_life: Union[int, None] = request.data.get('effective_life')
    #     # Save as draft or register
    #     asset_status: str = request.data.get('asset_status')
    #     data = {
    #         'user': user_pk,
    #         'asset_name': asset_name,
    #         'asset_number': asset_number,
    #         'purchase_date': purchase_date,
    #         'purchase_price': float(purchase_price) if purchase_price else None,
    #         'warranty_expiry': warranty_expiry,
    #         'serial_number': serial_number,
    #         'asset_type': asset_type,
    #         'region': region,
    #         'description': description,
    #         'depreciation_start_date': depreciation_start_date,
    #         'cost_limit': float(cost_limit) if cost_limit else None,
    #         'residual_value': float(residual_value) if residual_value else None,
    #         'depreciation_method': depreciation_method,
    #         'averaging_method': averaging_method,
    #         'rate': float(rate) if rate else None,
    #         'effective_life': float(effective_life) if effective_life else None,
    #         'asset_status': asset_status,
    #     }
    #     serializer: AssetsSerializer = AssetsSerializer(data=data)
    #     if serializer.is_valid():
    #         if depreciation_method == 'ST':
    #             book_value: Union[float, int] = StraightLine(data).calculate_depreciation()
    #         elif depreciation_method in ['100', '150', '200']:
    #             book_value: Union[float, int] = (DecliningBalanceBy100Or150Or200(data)
    #                                              .calculate_depreciation())
    #         elif depreciation_method == 'FD':
    #             book_value: Union[float, int] = FullDepreciation(data).calculate_depreciation()
    #         else:
    #             book_value: Union[float, int] = 0
    #         # Only if asset is registered
    #         if asset_status == 'RE':
    #             new_book_value: float = int(data.get('purchase_price')) - book_value
    #             date_object: date = datetime.strptime(data.get('depreciation_start_date'), '%Y-%m-%d').date()
    #             last_month_day: int = monthrange(date_object.year, date_object.month)[1]
    #             last_date: date = date(date_object.year, date_object.month, last_month_day)
    #             data: Dict[str, Union[int, str, float, None]] = {
    #                 **data,
    #                 'book_value': new_book_value,
    #             }
    #             asset = serializer.save()
    #             calculated_depreciation_serializer: CalculatedDepreciationSerializer = (
    #                 CalculatedDepreciationSerializer(data={
    #                     'asset': asset.pk,
    #                     'depreciation_of': book_value,
    #                     'depreciation_date': last_date
    #                 }))
    #             asset = Asset.objects.get(pk=asset.pk)
    #             asset.book_value = new_book_value
    #             asset.save()
    #             if calculated_depreciation_serializer.is_valid():
    #                 calculated_depreciation_serializer.save()
    #                 return Response(data=data, status=status.HTTP_200_OK)
    #             raise ValidationError(calculated_depreciation_serializer.errors)
    #     raise ValidationError(serializer.errors)

    @staticmethod
    def post(request, *args, **kwargs):
        user_pk: int = request.user.pk
        data = {
            'user': user_pk,
            'asset_name': request.data.get('asset_name'),
            'asset_number': request.data.get('asset_number'),
            'purchase_date': request.data.get('purchase_date'),
            'purchase_price': float(request.data.get('purchase_price')) if request.data.get('purchase_price') else None,
            'warranty_expiry': request.data.get('warranty_expiry'),
            'serial_number': request.data.get('serial_number'),
            'asset_type': request.data.get('asset_type_pk'),
            'region': request.data.get('region'),
            'description': request.data.get('description'),
            'depreciation_start_date': request.data.get('depreciation_start_date'),
            'cost_limit': float(request.data.get('cost_limit')) if request.data.get('cost_limit') else None,
            'residual_value': float(request.data.get('residual_value')) if request.data.get('residual_value') else None,
            'depreciation_method': request.data.get('depreciation_method'),
            'averaging_method': request.data.get('averaging_method'),
            'rate': float(request.data.get('rate')) if request.data.get('rate') else None,
            'effective_life': float(request.data.get('effective_life')) if request.data.get('effective_life') else None,
            'asset_status': request.data.get('asset_status'),
        }
        serializer: AssetsSerializer = AssetsSerializer(data=data)
        if serializer.is_valid():
            depreciation_method = data['depreciation_method']
            book_value = 0

            if depreciation_method in ['ST', '100', '150', '200', 'FD']:
                if depreciation_method == 'ST':
                    book_value = StraightLine(data).calculate_depreciation()
                elif depreciation_method in ['100', '150', '200']:
                    book_value = DecliningBalanceBy100Or150Or200(data).calculate_depreciation()
                elif depreciation_method == 'FD':
                    book_value = FullDepreciation(data).calculate_depreciation()

            if data['asset_status'] == 'RE':
                new_book_value = data['purchase_price'] - book_value
                depreciation_start_date = datetime.strptime(data['depreciation_start_date'], '%Y-%m-%d').date()
                last_month_day = monthrange(depreciation_start_date.year, depreciation_start_date.month)[1]
                last_date = date(depreciation_start_date.year, depreciation_start_date.month, last_month_day)
                data['book_value'] = new_book_value

                asset = serializer.save()
                asset.book_value = new_book_value
                asset.save()

                calculated_depreciation_serializer = CalculatedDepreciationSerializer(data={
                    'asset': asset.pk,
                    'depreciation_of': book_value,
                    'depreciation_date': last_date
                })

                if calculated_depreciation_serializer.is_valid():
                    calculated_depreciation_serializer.save()
                    return Response(data=data, status=status.HTTP_200_OK)
                raise ValidationError(calculated_depreciation_serializer.errors)

        raise ValidationError(serializer.errors)

    @staticmethod
    def put(request, *args, **kwargs):
        user = request.user
        asset_pk: int = request.data.get('asset_pk')
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
        # Edit as draft or register
        asset_status: str = request.data.get('asset_status')
        try:
            asset_obj: Union[QuerySet, Asset] = Asset.objects.get(pk=asset_pk, user=user)
            data = {
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
            serializer: AssetsSerializer = AssetsSerializer(asset_obj, data=data, partial=True)
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
                asset = serializer.save()
                if asset_status == 'RE':
                    new_book_value: float = int(data.get('purchase_price')) - book_value
                    date_object: date = datetime.strptime(data.get('depreciation_start_date'),
                                                          '%Y-%m-%d').date()
                    last_month_day: int = monthrange(date_object.year, date_object.month)[1]
                    last_date: date = date(date_object.year, date_object.month, last_month_day)
                    data: Dict[str, Union[int, str, float, None]] = {
                        **data,
                        'book_value': new_book_value,
                    }
                    # Delete old calculations
                    CalculatedDepreciation.objects.filter(asset=asset).delete()
                    calculated_depreciation_serializer: CalculatedDepreciationSerializer = (
                        CalculatedDepreciationSerializer(data={
                            'asset': asset.pk,
                            'depreciation_of': book_value,
                            'depreciation_date': last_date
                        }))
                    asset = Asset.objects.get(pk=asset.pk)
                    asset.book_value = new_book_value
                    asset.save()
                    if calculated_depreciation_serializer.is_valid():
                        # insert new calculations
                        calculated_depreciation_serializer.save()
                        # Edit on register
                        return Response(data=data, status=status.HTTP_200_OK)
                    raise ValidationError(calculated_depreciation_serializer.errors)
                else:
                    # Edit on draft
                    return Response(data=data, status=status.HTTP_200_OK)
            raise ValidationError(serializer.errors)
        except Asset.DoesNotExist:
            raise NotFound('Asset for this user do not exist.')

    @staticmethod
    def delete(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        asset_pks_list = str(asset_pk).split(',')
        Asset.objects.filter(user=user, pk__in=asset_pks_list).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        try:
            asset = Asset.objects.get(pk=asset_pk, user=user)
            if asset.asset_status == 'RE':
                serializer: AssetsGetSerializer = AssetsGetSerializer(asset)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                raise NotFound('Asset for this user do not exist.')
        except Asset.DoesNotExist:
            raise NotFound('Asset for this user do not exist.')


class AssetsRegisterView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        asset_pks_list = str(asset_pk).split(',')
        assets = Asset.objects.filter(user=user, pk__in=asset_pks_list)
        for asset in assets:
            depreciation_start_date: str = '{}-{}-{}'.format(asset.depreciation_start_date.year,
                                                             asset.depreciation_start_date.month,
                                                             asset.depreciation_start_date.day)
            data = {
                'asset_name': asset.asset_name,
                'asset_number': asset.asset_number,
                'purchase_date': asset.purchase_date,
                'purchase_price': float(asset.purchase_price) if asset.purchase_price else None,
                'warranty_expiry': asset.warranty_expiry,
                'serial_number': asset.serial_number,
                'asset_type': asset.asset_type,
                'region': asset.region,
                'description': asset.description,
                'depreciation_start_date': depreciation_start_date,
                'cost_limit': float(asset.cost_limit) if asset.cost_limit else None,
                'residual_value': float(asset.residual_value) if asset.residual_value else None,
                'depreciation_method': asset.depreciation_method,
                'averaging_method': asset.averaging_method,
                'rate': float(asset.rate) if asset.rate else None,
                'effective_life': float(asset.effective_life) if asset.effective_life else None,
            }
            if asset.depreciation_method == 'ST':
                book_value: Union[float, int] = StraightLine(data).calculate_depreciation()
            elif asset.depreciation_method in ['100', '150', '200']:
                book_value: Union[float, int] = (DecliningBalanceBy100Or150Or200(data)
                                                 .calculate_depreciation())
            elif asset.depreciation_method == 'FD':
                book_value: Union[float, int] = FullDepreciation(data).calculate_depreciation()
            else:
                book_value: Union[float, int] = 0
            new_book_value: float = int(data.get('purchase_price')) - book_value
            date_object: date = datetime.strptime(data.get('depreciation_start_date'), '%Y-%m-%d').date()
            last_month_day: int = monthrange(date_object.year, date_object.month)[1]
            last_date: date = date(date_object.year, date_object.month, last_month_day)
            # Delete old calculations
            CalculatedDepreciation.objects.filter(asset=asset).delete()
            calculated_depreciation_serializer: CalculatedDepreciationSerializer = (
                CalculatedDepreciationSerializer(data={
                    'asset': asset.pk,
                    'depreciation_of': book_value,
                    'depreciation_date': last_date
                }))
            asset.book_value = new_book_value
            asset.asset_status = 'RE'
            asset.save()
            if calculated_depreciation_serializer.is_valid():
                calculated_depreciation_serializer.save()
            else:
                continue
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetsDraftView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        asset_pks_list = str(asset_pk).split(',')
        assets = Asset.objects.filter(user=user, pk__in=asset_pks_list)
        for asset in assets:
            asset.book_value = 0
            asset.asset_status = 'DR'
            CalculatedDepreciation.objects.filter(asset=asset).delete()
            asset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListAssetsView(ListAPIView, PageNumberPagination):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AssetsListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['asset_name', 'asset_number', 'purchase_date', 'purchase_price']
    ordering = ['-pk']
    search_fields = ['asset_name', 'asset_number', 'purchase_date', 'purchase_price',
                     'warranty_expiry', 'serial_number', 'asset_type__asset_type',
                     'description', 'depreciation_start_date', 'cost_limit', 'residual_value',
                     'rate', 'effective_life']
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

    @staticmethod
    def get_list_of_dates(from_date: str, to_date: str) -> list:
        dates = [from_date, to_date]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        result = OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None)
                             for _ in xrange((end - start).days)).keys()
        last_dates = []
        for i in list(result):
            date_object: date = datetime.strptime(i, '%m-%Y').date()
            last_month_day: int = monthrange(date_object.year, date_object.month)[1]
            last_date: date = date(date_object.year, date_object.month, last_month_day)
            last_dates.append(last_date)
        return last_dates

    def post(self, request, *args, **kwargs):
        user = request.user
        start_date = str(AssetSetting.objects.get(user=user).start_date)
        to_date: str = request.data.get('to_date')
        list_of_dates: list = self.get_list_of_dates(start_date, to_date)
        assets = Asset.objects.filter(user=user, asset_status='RE')
        for asset in assets:
            # Delete old calculations
            CalculatedDepreciation.objects.filter(asset=asset).delete()
            date_: date
            for date_ in list_of_dates:
                depreciation_start_date: str = '{}-{}-1'.format(date_.year, date_.month)
                data = {
                    'asset_name': asset.asset_name,
                    'asset_number': asset.asset_number,
                    'purchase_date': asset.purchase_date,
                    'purchase_price': float(asset.purchase_price) if asset.purchase_price else None,
                    'warranty_expiry': asset.warranty_expiry,
                    'serial_number': asset.serial_number,
                    'asset_type': asset.asset_type,
                    'region': asset.region,
                    'description': asset.description,
                    'depreciation_start_date': depreciation_start_date,
                    'cost_limit': float(asset.cost_limit) if asset.cost_limit else None,
                    'residual_value': float(asset.residual_value) if asset.residual_value else None,
                    'depreciation_method': asset.depreciation_method,
                    'averaging_method': asset.averaging_method,
                    'rate': float(asset.rate) if asset.rate else None,
                    'effective_life': float(asset.effective_life) if asset.effective_life else None,
                }
                if asset.depreciation_method == 'ST':
                    book_value: Union[float, int] = StraightLine(data).calculate_depreciation()
                elif asset.depreciation_method in ['100', '150', '200']:
                    book_value: Union[float, int] = (DecliningBalanceBy100Or150Or200(data)
                                                     .calculate_depreciation())
                elif asset.depreciation_method == 'FD':
                    book_value: Union[float, int] = FullDepreciation(data).calculate_depreciation()
                else:
                    book_value: Union[float, int] = 0

                calculated_depreciation_serializer: CalculatedDepreciationSerializer = (
                    CalculatedDepreciationSerializer(data={
                        'asset': asset.pk,
                        'depreciation_of': book_value,
                        'depreciation_date': date_
                    }))
                if calculated_depreciation_serializer.is_valid():
                    calculated_depreciation_serializer.save()
                    # Get the new book value
                    asset.book_value = (int(data.get('purchase_price')) -
                                        (CalculatedDepreciation.objects.filter(asset=asset)
                                         .aggregate(Sum('depreciation_of'))).get('depreciation_of__sum'))
                    asset.save()
                else:
                    continue
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetsRollBackDepreciationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        roll_back_to: str = request.data.get('roll_back_to')
        roll_back_to_date: date = datetime.strptime(roll_back_to, '%Y-%m-%d').date()
        calculated_depreciations: Union[QuerySet, CalculatedDepreciation] = (CalculatedDepreciation.objects
                                                                             .filter(asset__user=user))
        i: Union[QuerySet, CalculatedDepreciation]
        for i in calculated_depreciations:
            if roll_back_to_date < i.depreciation_date:
                i.asset.book_value += i.depreciation_of
                i.asset.book_value = round(i.asset.book_value, 2)
                i.asset.save()
                i.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetsDisposeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # @staticmethod
    # def get(request, *args, **kwargs):
    #     user = request.user
    #     dispose_date: str = request.data.get('dispose_date')
    #     # dispose_date_obj: datetime = datetime.strptime(dispose_date, "%Y-%m-%d")
    #     sale_proceeds: float = request.data.get('sale_proceeds')
    #     sale_proceeds_account_pk: int = request.data.get('sale_proceeds_account_pk')
    #     depreciation_this_year: str = request.data.get('depreciation_this_year')
    #     asset_pk: Union[int, str] = request.data.get('asset_pk')
    #     data: Dict[str, Union[float, str]] = {}
    #     try:
    #         asset: Union[QuerySet, Asset, CalculatedDepreciation] = (
    #             Asset.objects.prefetch_related('calculated_depreciation_asset')
    #             .get(user=user, pk=asset_pk))
    #         accumulated_depreciation: Union[float, str] = ((CalculatedDepreciation.objects.filter(asset=asset_pk)
    #                                                         .aggregate(Sum('depreciation_of')))
    #                                                        .get('depreciation_of__sum'))
    #         # AD = All depreciation
    #         if depreciation_this_year == 'AD':
    #             depreciation_date: str = request.data.get('depreciation_date')
    #             dispose_asset = DisposeAsset2({
    #                 'user': user,
    #                 'dispose_date': dispose_date,
    #                 'sale_proceeds': sale_proceeds,
    #                 'proceeds_account_pk': sale_proceeds_account_pk,
    #                 'depreciation_date': depreciation_date,
    #                 'asset_pk': asset_pk
    #             })
    #             data = dispose_asset.calculate_journal()
    #             return Response(data, status=status.HTTP_200_OK)
    #         # ND = No depreciation
    #         else:
    #             purchase_date: str = '{}/{}/{}'.format(asset.purchase_date.day, asset.purchase_date.month,
    #                                                    asset.purchase_date.year)
    #             depreciated_to_obj: date = (CalculatedDepreciation.objects.filter(asset=asset_pk)
    #                                         .latest('depreciation_date').depreciation_date)
    #             depreciated_to: str = '{}/{}/{}'.format(depreciated_to_obj.day, depreciated_to_obj.month,
    #                                                     depreciated_to_obj.year)
    #             reversal_of_depreciation: Union[float, str] = ((CalculatedDepreciation.objects.filter(asset=asset_pk)
    #                                                             .filter(depreciation_date__gte=asset.purchase_date,
    #                                                                     depreciation_date__lte=depreciated_to_obj)
    #                                                             .aggregate(Sum('depreciation_of')))
    #                                                            .get('depreciation_of__sum'))
    #             data['cost'] = asset.purchase_price
    #             data['current_accumulated_depreciation'] = accumulated_depreciation
    #             data['reversal_of_depreciation_date'] = '{} to {}'.format(purchase_date, depreciated_to)
    #             data['reversal_of_depreciation_value'] = reversal_of_depreciation
    #             data['sale_proceeds'] = float(sale_proceeds)
    #             if asset.purchase_price == float(sale_proceeds):
    #                 return Response(data, status=status.HTTP_200_OK)
    #             elif asset.purchase_price < float(sale_proceeds):
    #                 data['capital_gain'] = float(sale_proceeds) - asset.purchase_price
    #                 return Response(data, status=status.HTTP_200_OK)
    #             else:
    #                 data['loss_on_disposal'] = asset.purchase_price - float(sale_proceeds)
    #                 return Response(data, status=status.HTTP_200_OK)
    #     except Asset.DoesNotExist:
    #         raise NotFound('Asset for this user do not exist.')

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        asset_pk = request.data.get('asset_pk')

        try:
            asset = Asset.objects.prefetch_related('calculated_depreciation_asset').get(user=user, pk=asset_pk)
        except Asset.DoesNotExist:
            return Response({'detail': 'Asset for this user does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        dispose_date = request.data.get('dispose_date')
        sale_proceeds = request.data.get('sale_proceeds')
        sale_proceeds_account_pk = request.data.get('sale_proceeds_account_pk')
        depreciation_this_year = request.data.get('depreciation_this_year')
        # data: Dict[str, Union[float, str]] = {}

        try:
            if depreciation_this_year == 'AD':
                depreciation_date = request.data.get('depreciation_date')
                dispose_asset = DisposeAsset2({
                    'user': user,
                    'dispose_date': dispose_date,
                    'sale_proceeds': sale_proceeds,
                    'proceeds_account_pk': sale_proceeds_account_pk,
                    'depreciation_date': depreciation_date,
                    'asset_pk': asset_pk
                })
                data = dispose_asset.calculate_journal()
            else:
                accumulated_depreciation = CalculatedDepreciation.objects.filter(asset=asset_pk) \
                    .aggregate(Sum('depreciation_of')).get('depreciation_of__sum')

                purchase_date = asset.purchase_date.strftime('%Y-%m-%d')
                depreciated_to_obj = CalculatedDepreciation.objects.filter(asset=asset_pk).latest('depreciation_date') \
                    .depreciation_date
                depreciated_to = depreciated_to_obj.strftime('%Y-%m-%d')

                reversal_of_depreciation = CalculatedDepreciation.objects.filter(asset=asset_pk) \
                    .filter(depreciation_date__gte=asset.purchase_date, depreciation_date__lte=depreciated_to_obj) \
                    .aggregate(Sum('depreciation_of')).get('depreciation_of__sum')

                data = {
                    'cost': asset.purchase_price,
                    'current_accumulated_depreciation': accumulated_depreciation,
                    'reversal_of_depreciation_date': f'{purchase_date} to {depreciated_to}',
                    'reversal_of_depreciation_value': reversal_of_depreciation,
                    'sale_proceeds': float(sale_proceeds)
                }

                if asset.purchase_price == float(sale_proceeds):
                    return Response(data, status=status.HTTP_200_OK)
                elif asset.purchase_price < float(sale_proceeds):
                    data['capital_gain'] = float(sale_proceeds) - asset.purchase_price
                else:
                    data['loss_on_disposal'] = asset.purchase_price - float(sale_proceeds)

        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        dispose_date: str = request.data.get('dispose_date')
        dispose_price: Union[int, str] = request.data.get('dispose_price')
        gain_on_disposal_account: Union[int, None] = request.data.get('gain_on_disposal_account_pk', None)
        capital_gain_account: Union[int, None] = request.data.get('capital_gain_account_pk', None)
        loss_on_disposal_account: Union[int, None] = request.data.get('loss_on_disposal_account_pk', None)
        gain_losses: int = request.data.get('gain_losses', None)
        try:
            asset = Asset.objects.get(pk=asset_pk, user=user)
            serializer: DisposedAssetsSerializer = DisposedAssetsSerializer(data={
                'asset': asset.pk,
                'disposal_date': dispose_date,
                'disposal_price': dispose_price,
                'capital_gain_on_disposal': gain_on_disposal_account,
                'gain_on_disposal': capital_gain_account,
                'loss_on_disposal': loss_on_disposal_account,
                'gain_losses': gain_losses,
            })
            if serializer.is_valid():
                serializer.save()
                asset.asset_status = 'DI'
                asset.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            raise ValidationError(serializer.errors)
        except Asset.DoesNotExist:
            raise NotFound('Asset for this user do not exist.')


class ListAssetsDisposedView(ListAPIView, PageNumberPagination):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AssetsDisposedListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['asset__asset_name', 'asset__asset_number', 'asset__asset_type__asset_type',
                       'asset__purchase_date', 'asset__purchase_price',
                       'disposal_date', 'disposal_price',
                       'gain_losses']
    ordering = ['-pk']
    search_fields = ['asset__asset_name', 'asset__asset_number', 'asset__purchase_date',
                     'asset__purchase_price', 'asset__warranty_expiry', 'asset__serial_number',
                     'asset__asset_type__asset_type', 'asset__description',
                     'asset__depreciation_start_date', 'asset__cost_limit', 'asset__residual_value',
                     'asset__rate', 'asset__effective_life', 'disposal_date', 'disposal_price',
                     'gain_losses']
    http_method_names = ('get',)
    page_size = 10

    def get_queryset(self) -> Union[QuerySet, DisposedAsset]:
        user = self.request.user
        return DisposedAsset.objects.filter(asset__user=user, asset__asset_status='DI')

    def list(self, request, *args, **kwargs):
        queryset: Union[QuerySet, DisposedAsset] = self.get_queryset()
        filter_queryset: QuerySet = self.filter_queryset(queryset)
        page = self.paginate_queryset(filter_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class AssetsUndisposeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        asset_pk: Union[int, str] = request.data.get('asset_pk')
        try:
            asset = Asset.objects.get(pk=asset_pk, user=user)
            asset.asset_status = 'RE'
            asset.book_value = asset.purchase_price
            asset.save()
            CalculatedDepreciation.objects.filter(asset=asset).delete()
            DisposedAsset.objects.filter(asset=asset).delete()
            return Response(status=status.HTTP_200_OK)
        except Asset.DoesNotExist:
            raise NotFound('Asset for this user do not exist.')


class AssetNumberView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        asset = Asset.objects.filter(user=user).latest('asset_number').asset_number
        asset_number = int(asset.split('-')[1]) + 1
        data = {
            "asset_prefix": asset.split('-')[0],
            "asset_number": "{:04d}".format(asset_number)
        }
        return Response(data=data, status=status.HTTP_200_OK)
