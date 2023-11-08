from django.urls import path
from .views import AssetView, AssetTypeView, AssetSettingsView

app_name = 'xero'

urlpatterns = [
    # POST : Attempt to add an Asset
    # GET : Get all assets
    path('assets/', AssetView.as_view()),
    # GET : Get one asset
    path('assets/<int:asset_id>/', AssetView.as_view()),
    # POST : Add an asset type
    # GET : Get asset types
    path('asset-types/', AssetTypeView.as_view()),
    # GET : Get asset settings
    path('asset-settings/', AssetSettingsView.as_view()),
]
