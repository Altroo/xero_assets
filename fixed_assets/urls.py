from django.urls import path
from .views import (AssetSettingsView, AssetTypesView, AssetsView,
                    ListAssetsView, AssetNumbersView, AssetRunDepreciationView,
                    AssetsRegisterView, AssetsDraftView, AssetsRollBackDepreciationView,
                    AssetsDisposeView, ListAssetsDisposedView, AssetsUndisposeView)

app_name = 'fixed_assets'

urlpatterns = [
    # POST : Add new Asset Settings
    # GET : Get user Asset Settings
    # PATCH : Edit user Asset Settings (start date or gain/lost accounts)
    path('asset-settings/', AssetSettingsView.as_view()),
    # POST : Add new Asset Type
    # GET : Get Asset type
    # PATCH : Edit Asset type
    path('asset-types/', AssetTypesView.as_view()),
    path('asset-types/<int:asset_type_pk>/', AssetTypesView.as_view()),
    # POST : Add new Asset
    # DELETE : Delete one or multiple assets
    # PATCH : Edit Asset status
    # PUT : Edit Asset
    # GET : Get Asset details
    path('assets/', AssetsView.as_view()),
    # POST : Mark asset as Register
    path('assets-register/', AssetsRegisterView.as_view()),
    # POST : Mark asset as Draft
    path('assets-draft/', AssetsDraftView.as_view()),
    # GET : Get Assets list filtered
    path('assets-list/', ListAssetsView.as_view()),
    # GET : Tab asset_status numbers
    path('asset-numbers/', AssetNumbersView.as_view()),
    # POST : Run depreciation
    path('asset-run-depreciation/', AssetRunDepreciationView.as_view()),
    # POST : Run rollback
    path('asset-run-rollback/', AssetsRollBackDepreciationView.as_view()),
    # GET : Dispose Asset details
    # POST : Dispose Asset
    path('asset-dispose/', AssetsDisposeView.as_view()),
    # POST : Undispose Asset
    path('asset-undispose/', AssetsUndisposeView.as_view()),
    # GET : Get disposed assets list
    path('asset-dispose-list/', ListAssetsDisposedView.as_view()),
]
