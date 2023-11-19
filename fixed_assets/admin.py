from django.contrib.admin import ModelAdmin, site
from .models import AssetSetting, AssetAccount, AssetType, Asset


class CustomAdminParent:
    list_display_links = ('pk',)
    ordering = ('-pk',)


# AssetSetting
class CustomSettingAdmin(ModelAdmin, CustomAdminParent):
    search_fields = ('pk', 'user')
    list_display = ('pk', 'user', 'start_date', 'capital_gain_on_disposal',
                    'gain_on_disposal', 'loss_on_disposal')


# AssetAccount
class CustomAssetAccountAdmin(ModelAdmin, CustomAdminParent):
    search_fields = ('pk', 'account_type_code', 'tax')
    list_display = ('pk', 'account_type_code', 'tax')


class CustomAssetTypeAdmin(ModelAdmin, CustomAdminParent):
    search_fields = ('pk', 'user', 'asset_type',
                     'asset_account__account_type_code',
                     'accumulated_depreciation_account__account_type_code',
                     'depreciation_expense_account__account_type_code',
                     'depreciation_method',
                     'averaging_method',
                     'rate',
                     'effective_life',
                     )
    list_display = ('pk', 'user', 'asset_type', 'asset_account',
                    'accumulated_depreciation_account',
                    'depreciation_expense_account',
                    'depreciation_method', 'averaging_method',
                    'rate', 'effective_life',)


class CustomAssetAdmin(ModelAdmin, CustomAdminParent):
    search_fields = ('pk', 'user', 'asset_name', 'asset_number',
                     'purchase_date', 'purchase_price', 'warranty_expiry',
                     'serial_number', 'asset_type__asset_type', 'region', 'description', 'depreciation_start_date',
                     'cost_limit', 'residual_value', 'asset_status')
    list_display = ('pk', 'user', 'asset_name', 'depreciation_method', 'averaging_method', 'rate', 'effective_life',
                    'asset_status')
    list_filter = ('asset_status', 'warranty_expiry', 'region')


# class CustomRegionAdmin(ModelAdmin):
#     search_fields = ('pk', 'region_name')
#     list_display = ('pk', 'region_name')
#     list_display_links = ('pk',)
#     ordering = ('-pk',)
#     list_filter = ('start_date',)
#     date_hierarchy = 'start_date'


site.register(AssetSetting, CustomSettingAdmin)
site.register(AssetAccount, CustomAssetAccountAdmin)
site.register(AssetType, CustomAssetTypeAdmin)
site.register(Asset, CustomAssetAdmin)
# site.register(Region, CustomRegionAdmin)
