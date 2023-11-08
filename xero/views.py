from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.assets import AssetApi, Asset, BookDepreciationSetting, AssetType
from xero_python.exceptions import AccountingBadRequestException
from xero_assets.settings import XERO_CLIENT_ID, XERO_CLIENT_SECRET, DEBUG

# configure api_client for use with xero-python sdk client
api_client = ApiClient(
    Configuration(
        debug=DEBUG,
        oauth2_token=OAuth2Token(
            client_id=XERO_CLIENT_ID, client_secret=XERO_CLIENT_SECRET
        ),
    ),
    pool_threads=1,
)

# token = {
#     "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFDQUY4RTY2NzcyRDZEQzAyOEQ2NzI"
#                     "2RkQwMjYxNTgxNTcwRUZDMTkiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJISy1PWm5"
#                     "jdGJjQW8xbkp2MENZVmdWY09fQmsifQ.eyJuYmYiOjE2OTk0NjMxNTYsImV4c"
#                     "CI6MTY5OTQ2MzQ1NiwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS54ZXJvLmNvbSI"
#                     "sImF1ZCI6IjQ5Q0ZCMUFBMUQzMzQxRDVCQjlCODU0RjM5NEJDOEREIiwiaWF0I"
#                     "joxNjk5NDYzMTU2LCJhdF9oYXNoIjoicko1NFJjVC1hR25Oa0pORmQ5THZrQSIs"
#                     "InNpZCI6IjI0ZDhkMWNiNGRlMDQwYTA4MDcyZjQyMzBjYjQ5NDZjIiwic3ViIjoi"
#                     "ZjM2ZDA5Njg1ZjIwNTE2ODhlNzNkMjFkMzc3NzUxYzMiLCJhdXRoX3RpbWUiOjE2O"
#                     "Tk0NjI5MzAsInhlcm9fdXNlcmlkIjoiZDI2MTgyY2MtOWZmZC00NzI0LThlZWEtNT"
#                     "IyYjljZDRjNjAzIiwiZ2xvYmFsX3Nlc3Npb25faWQiOiIyNGQ4ZDFjYjRkZTA0MGEw"
#                     "ODA3MmY0MjMwY2I0OTQ2YyIsInByZWZlcnJlZF91c2VybmFtZSI6InlvdW5lc3MuZWx"
#                     "hbGFtaTAyQGdtYWlsLmNvbSIsImVtYWlsIjoieW91bmVzcy5lbGFsYW1pMDJAZ21haW"
#                     "wuY29tIiwiZ2l2ZW5fbmFtZSI6IllvdW5lc3MiLCJmYW1pbHlfbmFtZSI6IkVsIEFsYW"
#                     "1pIiwibmFtZSI6IllvdW5lc3MgRWwgQWxhbWkiLCJhbXIiOlsicHdkIiwibWZhIiwib3R"
#                     "wIl19.c6feUZSGA4j_wu7Sl9-q-yyvDmMEtDgDAexceVmaJh_NrUzovkOwGh7V5dUHH3B"
#                     "GAKbSUhuE0gkYvhdlnhpaI5uYb6_Tfhuvrelb8ebHurufLgyBkpHsQiWkhAX29nl2vV3GI"
#                     "-Y-iQoDRWTDBBdqExRkBX3TAYBH4j4A_HyQutX7tGrtBTJ-HOtanHeh5fL2J4yrMqRJ9Qv"
#                     "jxk2cxSq0DmGfp16hfZai0z1hgf8kEJMJbpPncypwD30qIeRo4hsYK8Z4yX2D3GtAgL2ga5"
#                     "8k_7igRPnZrDArs150lDIlG8yl5a8cwKlhr6VjWawstcOewV2P3iM14OUaejNqp4ZMtw",
#     "expires_at": "",
#     "expires_in": "",
#     "refresh_token": "",
#     "scope": [
#         "openid",
#         "profile",
#         "email",
#         "assets",
#         "projects",
#         "offline_access",
#     ],
#     "token_type": "Bearer"
# }
api_client.set_oauth2_token("YOUR ACCESS TOKEN")


class AssetView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        api_instance = AssetApi(api_client)
        # 6bf6e95d-4af5-4648-9fc3-9cb53f5ea7c6
        xero_tenant_id = request.data.get('xero_tenant_id')

        asset = Asset(
            asset_name=request.data.get('asset_name'),
            asset_number=request.data.get('asset_number'),
            asset_status=request.data.get('asset_status'))

        try:
            api_response = api_instance.create_asset(xero_tenant_id, asset)
            return Response(data=api_response.data, status=status.HTTP_200_OK)
        except AccountingBadRequestException as e:
            return Response(data=e.error_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get(request, *args, **kwargs):
        api_instance = AssetApi(api_client)
        xero_tenant_id = request.data.get('xero_tenant_id')
        asset_id = kwargs.get('asset_id')
        order_by = request.data.get('order_by')
        page = request.data.get('page')
        page_size = request.data.get('page_size')
        status_ = request.data.get('status')
        sort_direction = request.data.get('sort_direction')
        filter_by = request.data.get('filter_by')
        try:
            if asset_id:
                api_response = api_instance.get_asset_by_id(xero_tenant_id, asset_id)
            else:
                api_response = api_instance.get_assets(xero_tenant_id, status_, page, page_size, order_by,
                                                       sort_direction, filter_by)
            return Response(data=api_response.data, status=status.HTTP_200_OK)
        except AccountingBadRequestException as e:
            return Response(data=e.error_data, status=status.HTTP_400_BAD_REQUEST)


class AssetTypeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        api_instance = AssetApi(api_client)
        xero_tenant_id = request.data.get('xero_tenant_id')

        book_depreciation_setting = BookDepreciationSetting(
            depreciation_method=request.data.get('depreciation_method'),
            averaging_method=request.data.get('averaging_method'),
            depreciation_rate=request.data.get('depreciation_rate'),
            depreciation_calculation_method=request.data.get('depreciation_calculation_method'))

        asset_type = AssetType(
            asset_type_name=request.data.get('asset_type_name'),
            fixed_asset_account_id=request.data.get('fixed_asset_account_id'),
            depreciation_expense_account_id=request.data.get('depreciation_expense_account_id'),
            accumulated_depreciation_account_id=request.data.get('accumulated_depreciation_account_id'),
            book_depreciation_setting=book_depreciation_setting)

        try:
            api_response = api_instance.create_asset_type(xero_tenant_id, asset_type)
            return Response(data=api_response.data, status=status.HTTP_200_OK)
        except AccountingBadRequestException as e:
            return Response(data=e.error_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get(request, *args, **kwargs):
        api_instance = AssetApi(api_client)
        xero_tenant_id = request.data.get('xero_tenant_id')
        try:
            api_response = api_instance.get_asset_types(xero_tenant_id)
            return Response(data=api_response.data, status=status.HTTP_200_OK)
        except AccountingBadRequestException as e:
            return Response(data=e.error_data, status=status.HTTP_400_BAD_REQUEST)


class AssetSettingsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        api_instance = AssetApi(api_client)
        xero_tenant_id = request.data.get('xero_tenant_id')
        try:
            api_response = api_instance.get_asset_settings(xero_tenant_id)
            return Response(data=api_response.data, status=status.HTTP_200_OK)
        except AccountingBadRequestException as e:
            return Response(data=e.error_data, status=status.HTTP_400_BAD_REQUEST)
