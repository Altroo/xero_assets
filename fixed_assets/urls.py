from django.urls import path
from .views import AssetSettingsView, AssetTypesView, AssetsView

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
    # GET : Get one asset or assets list
    # DELETE : Delete one or multiple assets
    # PATCH : Edit Asset status
    path('assets/', AssetsView.as_view()),
]
