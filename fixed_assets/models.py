from auth.models import CustomUser
from django.db.models import (Model, CharField, ForeignKey,
                              CASCADE, OneToOneField, IntegerField,
                              FloatField, PositiveIntegerField, TextField, DateField, SET_NULL)


# class Region(Model):
#     region_name = CharField(verbose_name='Region Name', max_length=255, unique=True)
#
#     def __str__(self):
#         return '{}'.format(self.region_name)
#
#     class Meta:
#         verbose_name = 'Region'
#         verbose_name_plural = 'Regions'


class AccountType:
    # CATEGORY_CHOICES = (
    #     ('AS', 'Assets'),
    #     ('EQ', 'Equity'),
    #     ('EX', 'Expenses'),
    #     ('LI', 'Liabilities'),
    #     ('RE', 'Revenue'),
    # )
    TAX_CHOICES = (
        ('ES', 'Exempt Sales 0%'),
        ('MP', 'MB - GST / RST on Purchasses 12%'),
        ('MS', 'MB - GST / RST on Sales 12%'),
        ('TE', 'Tax Exempt 0%'),
        ('TC', 'Tax on Consulting 8.25%'),
        ('TG', 'Tax on Goods 8.75%'),
        ('TP', 'Tax on Purchases 8.25%'),
    )
    DEPRECIATION_CHOICES = (
        ('ND', 'No Depreciation'),
        ('ST', 'Straight Line'),
        ('100', 'Diminishing Value 100'),
        ('150', 'Diminishing Value 150'),
        ('200', 'Diminishing Value 200'),
        ('FD', 'Full Depreciation'),
    )
    AVERAGING_CHOICES = (
        ('AD', 'Actual Days'),
        ('FM', 'Full Month'),
    )
    STATUS_CHOICES = (
        ('RE', 'Registered'),
        ('DR', 'Draft'),
        ('DI', 'Disposed'),
    )
    # TODO needs to be seperated
    REGION_CHOICES = (
        ('E', 'East Side'),
        ('N', 'North'),
        ('S', 'South'),
        ('W', 'West Coast'),
    )


class AssetAccount(Model):
    account_name = CharField(verbose_name='Account name', max_length=255, blank=True, null=True, default=None)
    account_type_code = CharField(verbose_name='Account Type code', max_length=15, unique=True)
    tax = CharField(verbose_name='Tax', choices=AccountType.TAX_CHOICES, default='ES', max_length=2)

    def __str__(self):
        return '{} - {}'.format(self.account_type_code, self.tax)

    class Meta:
        verbose_name = 'Asset Account'
        verbose_name_plural = 'Asset Accounts'


class AssetSetting(Model):
    user = OneToOneField(CustomUser, on_delete=CASCADE, verbose_name='User', related_name="asset_setting_user")
    start_date = DateField(verbose_name='Start Date', null=True, blank=True)
    capital_gain_on_disposal = ForeignKey(AssetAccount, on_delete=SET_NULL, verbose_name='Capital Gain on Disposal',
                                          related_name='capital_gain_on_disposal_setting', null=True,
                                          blank=True, default=None)
    gain_on_disposal = ForeignKey(AssetAccount, on_delete=SET_NULL, verbose_name='Gain on Disposal',
                                  related_name='gain_on_disposal_setting', null=True, blank=True, default=None)
    loss_on_disposal = ForeignKey(AssetAccount, on_delete=SET_NULL, verbose_name='Loss on Disposal',
                                  related_name='loss_on_disposal_setting', null=True, blank=True, default=None)

    def __str__(self):
        return "{} - {}".format(self.pk, self.start_date)

    class Meta:
        verbose_name = "Asset Setting"
        verbose_name_plural = "Asset Settings"


class AssetType(Model):
    user = ForeignKey(CustomUser, on_delete=CASCADE, verbose_name='User', related_name="asset_type_user",
                      null=True, default=None, blank=True)
    asset_type = CharField(verbose_name='Asset Type', max_length=255, null=True, default=None, blank=True)
    asset_account = ForeignKey(AssetAccount, on_delete=CASCADE, verbose_name='Asset Account',
                               related_name='asset_account')
    accumulated_depreciation_account = ForeignKey(AssetAccount, on_delete=CASCADE,
                                                  verbose_name='Accumulated Depreciation Account',
                                                  related_name='accumulated_depreciation_account')
    depreciation_expense_account = ForeignKey(AssetAccount, on_delete=CASCADE,
                                              verbose_name='Depreciation Expense Account',
                                              related_name='depreciation_expense_account')
    depreciation_method = CharField(verbose_name='Depreciation Method',
                                    choices=AccountType.DEPRECIATION_CHOICES, default='ND', max_length=3)
    averaging_method = CharField(verbose_name='Averaging Method',
                                 choices=AccountType.AVERAGING_CHOICES, default='AD', max_length=2)
    rate = FloatField(verbose_name='Rate', blank=True, null=True, default=None)
    effective_life = PositiveIntegerField(verbose_name='Effective Life', blank=True, null=True, default=None)

    def __str__(self):
        return '{} - {} - {}'.format(self.asset_type, self.rate, self.effective_life)

    class Meta:
        verbose_name = 'Asset Type'
        verbose_name_plural = 'Asset Types'


class Asset(Model):
    user = ForeignKey(CustomUser, on_delete=CASCADE, verbose_name='User', related_name="asset_user")
    asset_name = CharField(verbose_name='Asset Name', max_length=255, null=True, default=None, blank=True)
    asset_number = CharField(verbose_name='Asset Number', max_length=255, null=True, blank=True, unique=True)
    purchase_date = DateField(verbose_name='Purchase Date', null=True, blank=True)
    purchase_price = FloatField(verbose_name='Purchase Price', blank=True, null=True)
    warranty_expiry = DateField(verbose_name='Warranty Expiry', null=True, blank=True)
    serial_number = CharField(verbose_name='Serial number', max_length=255, null=True, default=None, blank=True)
    asset_type = ForeignKey(AssetType, on_delete=CASCADE, verbose_name='Asset type', related_name='asset_asset_type')
    region = CharField(verbose_name='Region', choices=AccountType.REGION_CHOICES, default='E', max_length=1)
    description = TextField(verbose_name='Description', default=None, null=True, blank=True)
    # Auto-filled from asset_type
    depreciation_start_date = DateField(verbose_name='Depreciation Start Date', null=True, blank=True)
    cost_limit = FloatField(verbose_name='Cost Limit', blank=True, null=True)
    residual_value = FloatField(verbose_name='Residual Value', blank=True, null=True)
    depreciation_method = CharField(verbose_name='Depreciation Method',
                                    choices=AccountType.DEPRECIATION_CHOICES, default='ND', max_length=3)
    averaging_method = CharField(verbose_name='Averaging Method',
                                 choices=AccountType.AVERAGING_CHOICES, default='AD', max_length=2)
    rate = FloatField(verbose_name='Rate', blank=True, null=True)
    effective_life = PositiveIntegerField(verbose_name='Effective Life', blank=True, null=True)
    asset_status = CharField(verbose_name='Asset Status', choices=AccountType.STATUS_CHOICES, default='RE',
                             max_length=2)
    book_value = FloatField(verbose_name='Book value', blank=True, null=True, default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.asset_name, self.rate, self.effective_life)

    class Meta:
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'


class CalculatedDepreciation(Model):
    asset = ForeignKey(Asset, on_delete=CASCADE, verbose_name='Asset', related_name="calculated_depreciation_asset")
    depreciation_of = FloatField(verbose_name='Depreciation of', blank=True, null=True)
    depreciation_date = DateField(verbose_name='Depreciation Date', null=True, blank=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.asset.asset_name, self.depreciation_of, self.depreciation_date)

    class Meta:
        verbose_name = 'Calculated Depreciation'
        verbose_name_plural = 'Calculated Depreciations'
        unique_together = (('asset', 'depreciation_date'),)
