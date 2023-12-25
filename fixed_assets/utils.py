from collections import OrderedDict
from typing import Union, Literal, List, Dict, Any
from datetime import date, datetime, timedelta
from calendar import isleap, monthrange

from cffi.backend_ctypes import xrange
from django.db.models import QuerySet, Sum
from rest_framework.exceptions import NotFound

from .models import Asset, CalculatedDepreciation


class Init:
    def __init__(self, kwargs):
        self.kwargs: Dict[str, Any] = kwargs
        self.start_date: str = kwargs.get('depreciation_start_date')
        self.purchase_price: Union[float, int] = kwargs.get('purchase_price')
        self.cost_limit: Union[float, int] = kwargs.get('cost_limit', 0)
        self.residual_value: Union[float, int] = kwargs.get('residual_value', 0)
        self.averaging_method: Literal['FM', 'AD'] = kwargs.get('averaging_method')
        self.rate: Union[float, int, bool] = kwargs.get('rate', False)
        self.effective_life: Union[float, int, bool] = kwargs.get('effective_life', False)
        self.depreciation_method: Union[Literal['100', '150', '200'], None] = kwargs.get('depreciation_method', None)

    def days_in_year(self) -> int:
        year: List[str] = str(self.start_date).split('-')
        return 365 + isleap(int(year[0]))

    def number_of_days_in_month(self) -> int:
        date_object: date = datetime.strptime(str(self.start_date).split(' ')[0], '%Y-%m-%d').date()
        last_month_day: int = monthrange(date_object.year, date_object.month)[1]
        last_date: date = date(date_object.year, date_object.month, last_month_day)
        delta: timedelta = last_date - date_object
        # return delta.days if delta.days > 0 else 1
        return max(delta.days, 1)  # Ensure the result is at least 1 to avoid division by zero


class StraightLine(Init):
    def calculate_depreciation(self) -> Union[int, float]:
        result: float = 0.00
        # Rate + Full month
        if self.rate and self.averaging_method == 'FM':
            # With cost_limit
            if self.cost_limit:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((self.cost_limit - self.residual_value) * self.rate) / 100) / 12
                # Without residual value
                else:
                    result: Union[int, float] = ((self.cost_limit * self.rate) / 100) / 12
            # Without cost limit
            else:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((self.purchase_price - self.residual_value) * self.rate) / 100) / 12
                # Without residual value
                else:
                    result: Union[int, float] = ((self.purchase_price * self.rate) / 100) / 12
        # Rate + Actual days
        elif self.rate and self.averaging_method == 'AD':
            # With cost_limit
            if self.cost_limit:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = ((((self.cost_limit - self.residual_value) * self.rate) / 100)
                                                 / (self.days_in_year() * self.number_of_days_in_month()))
                # Without residual value
                else:
                    result: Union[int, float] = (((self.cost_limit * self.rate) / 100)
                                                 / (self.days_in_year() * self.number_of_days_in_month()))
            # Without cost limit
            else:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = ((((self.purchase_price - self.residual_value) * self.rate) / 100)
                                                 / (self.days_in_year() * self.number_of_days_in_month()))
                # Without residual value
                else:
                    result: Union[int, float] = ((self.purchase_price * (self.rate / 100) / self.days_in_year()) *
                                                 self.number_of_days_in_month())
        # Effective life + full month
        if self.effective_life and self.averaging_method == 'FM':
            # With cost_limit
            if self.cost_limit:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = ((self.cost_limit - self.residual_value) / self.effective_life) / 12
                # Without residual value
                else:
                    result: Union[int, float] = (self.cost_limit * self.effective_life) / 12
            # Without cost limit
            else:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = ((self.purchase_price - self.residual_value) / self.effective_life) / 12
                # Without residual value
                else:
                    result: Union[int, float] = (self.purchase_price / self.effective_life) / 12
        # Effective life + Actual days
        elif self.effective_life and self.averaging_method == 'AD':
            # With cost_limit
            if self.cost_limit:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((self.cost_limit - self.residual_value) / self.effective_life)
                                                 / (self.days_in_year() * self.number_of_days_in_month()))
                # Without residual value
                else:
                    result: Union[int, float] = ((self.cost_limit / self.effective_life)
                                                 / (self.days_in_year() * self.number_of_days_in_month()))
            # Without cost limit
            else:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((self.purchase_price - self.residual_value) / self.effective_life)
                                                 / (self.days_in_year() * self.number_of_days_in_month()))
                # Without residual value
                else:
                    # print('purchase_price : ', self.purchase_price)
                    # print('effective_life : ', self.effective_life)
                    # print('days_in_year : ', self.days_in_year())
                    # print('number_of_days_in_month : ', self.number_of_days_in_month())
                    result: Union[int, float] = (((self.purchase_price / self.effective_life) / self.days_in_year()) *
                                                 self.number_of_days_in_month())
            # print(result)
        return round(result, 2)


class FullDepreciation(Init):
    @staticmethod
    def calculate_depreciation() -> Union[int, float]:
        result: float = 0.00
        return result


class DecliningBalanceBy100Or150Or200(Init):
    def get_declining_balance(self):
        if self.depreciation_method == '150':
            return 1.5
        elif self.depreciation_method == '200':
            return 2
        else:
            return 1

    def calculate_depreciation(self) -> Union[int, float]:
        result: float = 0.00
        declining_balance: int = self.get_declining_balance()
        # Effective life + full month
        if self.averaging_method == 'FM':
            # With cost_limit
            if self.cost_limit:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = ((((self.cost_limit - self.residual_value) / self.effective_life) / 12)
                                                 * declining_balance)
                # Without residual value
                else:
                    result: Union[int, float] = ((self.cost_limit * self.effective_life) / 12) * declining_balance
            # Without cost limit
            else:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((self.purchase_price - self.residual_value) /
                                                  self.effective_life) / 12) * declining_balance
                # Without residual value
                else:
                    result: Union[int, float] = ((self.purchase_price / self.effective_life) / 12) * declining_balance
        # Effective life + Actual days
        elif self.averaging_method == 'AD':
            # With cost_limit
            if self.cost_limit:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((((self.cost_limit - self.residual_value) / self.effective_life)
                                                   / (self.days_in_year() * self.number_of_days_in_month()))) *
                                                 declining_balance)
                # Without residual value
                else:
                    result: Union[int, float] = ((((self.cost_limit / self.effective_life)
                                                   / (self.days_in_year() * self.number_of_days_in_month()))) *
                                                 declining_balance)
            # Without cost limit
            else:
                # with residual value
                if self.residual_value:
                    result: Union[int, float] = (((((self.purchase_price - self.residual_value) / self.effective_life)
                                                   / (self.days_in_year() * self.number_of_days_in_month()))) *
                                                 declining_balance)
                # Without residual value
                else:
                    result: Union[int, float] = ((((self.purchase_price / self.effective_life) / self.days_in_year()) *
                                                  self.number_of_days_in_month())) * declining_balance
        return round(result, 2)


class DisposeAsset:
    def __init__(self, kwargs):
        self.kwargs: Dict[str, Any] = kwargs
        self.user = kwargs['user']
        self.dispose_date = kwargs['dispose_date']
        self.sale_proceeds = kwargs['sale_proceeds']
        self.proceeds_account_pk = kwargs['proceeds_account_pk']
        self.depreciation_date = kwargs['depreciation_date']
        self.asset_pk = kwargs['asset_pk']
        self.depreciation_to_be_posted_date = None
        self.reversal_of_depreciation_date_start: Union[date, None] = None
        self.reversal_of_depreciation_date_end: Union[date, None] = None

    @staticmethod
    def generate_data_for_depreciation(asset: Union[QuerySet, Asset, CalculatedDepreciation],
                                       new_last_date: datetime) -> dict:
        return {
            'asset_name': asset.asset_name,
            'asset_number': asset.asset_number,
            'purchase_date': asset.purchase_date,
            'purchase_price': float(asset.purchase_price) if asset.purchase_price else None,
            'warranty_expiry': asset.warranty_expiry,
            'serial_number': asset.serial_number,
            'asset_type': asset.asset_type,
            'region': asset.region,
            'description': asset.description,
            'depreciation_start_date': new_last_date,
            'cost_limit': float(asset.cost_limit) if asset.cost_limit else None,
            'residual_value': float(asset.residual_value) if asset.residual_value else None,
            'depreciation_method': asset.depreciation_method,
            'averaging_method': asset.averaging_method,
            'rate': float(asset.rate) if asset.rate else None,
            'effective_life': float(asset.effective_life) if asset.effective_life else None,
        }

    def get_dispose_date(self) -> datetime:
        return datetime.strptime(self.dispose_date, "%Y-%m-%d")

    def get_depreciation_date(self) -> datetime:
        return datetime.strptime(self.depreciation_date, "%Y-%m-%d")

    def get_last_depreciation_date(self) -> datetime:
        return datetime.combine((CalculatedDepreciation.objects.filter(asset=self.asset_pk, asset__user=self.user)
                                 .latest('depreciation_date').depreciation_date),
                                datetime.min.time())

    def get_accumulated_depreciation(self) -> float:
        return ((CalculatedDepreciation.objects.filter(asset=self.asset_pk, asset__user=self.user)
                 .aggregate(Sum('depreciation_of')))
                .get('depreciation_of__sum'))

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

    def get_accumulated_depreciations_till_date(self, asset: Union[QuerySet, Asset, CalculatedDepreciation]):
        accumulated_depreciation: float = ((CalculatedDepreciation.objects.filter(asset=self.asset_pk,
                                                                                  asset__user=self.user)
                                            .aggregate(Sum('depreciation_of')))
                                           .get('depreciation_of__sum'))
        book_value = 0
        data_: dict = self.generate_data_for_depreciation(asset, self.get_depreciation_date())
        start_date = (CalculatedDepreciation.objects.filter(asset=self.asset_pk, asset__user=self.user)
                      .latest('depreciation_date').depreciation_date)
        start_date_str: str = str(start_date)
        list_of_dates: list = self.get_list_of_dates(start_date_str, self.depreciation_date)
        for date_ in list_of_dates:
            if self.get_depreciation_date() < datetime.combine(date_, datetime.min.time()):
                list_of_dates.remove(date_)
        if list_of_dates.__len__() == 0:
            self.reversal_of_depreciation_date_start = datetime.strptime(
                '{}-{}-1'.format(start_date.year, start_date.month), "%Y-%m-%d")
            self.reversal_of_depreciation_date_end = self.get_depreciation_date()
        for date_ in list_of_dates:
            self.depreciation_to_be_posted_date = date_
            if asset.depreciation_method == 'ST':
                book_value: Union[float, int] = book_value + StraightLine(data_).calculate_depreciation()
            elif asset.depreciation_method in ['100', '150', '200']:
                book_value: Union[float, int] = book_value + (DecliningBalanceBy100Or150Or200(data_)
                                                              .calculate_depreciation())
            elif asset.depreciation_method == 'FD':
                book_value: Union[float, int] = book_value + FullDepreciation(data_).calculate_depreciation()
            else:
                book_value: Union[float, int] = book_value + 0
        return accumulated_depreciation, book_value

    def dispose_till_last_date(self, asset: Union[QuerySet, Asset, CalculatedDepreciation]) -> dict:
        data: Dict[str, Union[float, str]] = {
            'cost': asset.purchase_price,
            'current_accumulated_depreciation': self.get_accumulated_depreciation(),
            'sale_proceeds': float(self.sale_proceeds)
        }
        # Case 1 : price == sale price
        if asset.purchase_price == float(self.sale_proceeds):
            data['gain_on_disposal'] = self.get_accumulated_depreciation()
        # Case 2 : price < sale price
        elif asset.purchase_price < float(self.sale_proceeds):
            data['gain_on_disposal'] = self.get_accumulated_depreciation()
            data['capital_gain'] = float(self.sale_proceeds) - asset.purchase_price
        # Case 3 : price > sale price
        else:
            if (asset.purchase_price - float(self.sale_proceeds) - self.get_accumulated_depreciation()) > 0:
                data['loss_on_disposal'] = (asset.purchase_price - float(self.sale_proceeds) -
                                            self.get_accumulated_depreciation())
        return data

    def dispose_with_extra_days(self, asset: Union[QuerySet, Asset, CalculatedDepreciation]) -> dict:
        accumulated_depreciation, book_value = self.get_accumulated_depreciations_till_date(asset)
        data: Dict[str, Union[float, str]] = {
            'cost': asset.purchase_price,
            'current_accumulated_depreciation': accumulated_depreciation,
        }
        if self.get_last_depreciation_date() != datetime.combine(self.depreciation_to_be_posted_date,
                                                                 datetime.min.time()):
            data['depreciation_to_be_posted'] = accumulated_depreciation
            data['depreciation_to_be_posted_date'] = self.depreciation_to_be_posted_date
        data['sale_proceeds'] = float(self.sale_proceeds)
        # Case 1 : price == sale price
        gain_on_disposal: float = (float(self.sale_proceeds) + book_value) - asset.purchase_price

        if asset.purchase_price == float(self.sale_proceeds):
            data['gain_on_disposal'] = book_value
        # Case 2 : price < sale price
        elif asset.purchase_price < float(self.sale_proceeds):
            data['gain_on_disposal'] = book_value
            data['capital_gain'] = float(self.sale_proceeds) - asset.purchase_price
        # Case 3 : price > sale price
        else:
            if gain_on_disposal > 0:
                data['gain_on_disposal'] = gain_on_disposal
            else:
                data['loss_on_disposal'] = abs(gain_on_disposal)
        return data

    def dispose_with_less_days(self, asset: Union[QuerySet, Asset, CalculatedDepreciation]) -> dict:
        accumulated_depreciation, book_value = self.get_accumulated_depreciations_till_date(asset)
        data: Dict[str, Union[float, str]] = {
            'cost': asset.purchase_price,
            'current_accumulated_depreciation': accumulated_depreciation,
        }
        if (self.reversal_of_depreciation_date_start < self.reversal_of_depreciation_date_end <
                self.get_last_depreciation_date()):
            # 24-01-31
            reversal_from = "{}/{}/{}".format(self.reversal_of_depreciation_date_start.year,
                                              self.reversal_of_depreciation_date_start.month,
                                              self.reversal_of_depreciation_date_start.day)
            reversal_to = "{}/{}/{}".format(self.get_last_depreciation_date().year,
                                            self.get_last_depreciation_date().month,
                                            self.get_last_depreciation_date().day)
            reversal_date = '{} to {}'.format(reversal_from, reversal_to)
            data['reversal_of_depreciation'] = accumulated_depreciation
            data['reversal_of_depreciation_date'] = reversal_date
        data['sale_proceeds'] = float(self.sale_proceeds)
        # Case 1 : price == sale price
        gain_on_disposal: float = (float(self.sale_proceeds) + book_value) - asset.purchase_price
        if asset.purchase_price == float(self.sale_proceeds):
            if book_value > 0:
                data['gain_on_disposal'] = book_value
        # Case 2 : price < sale price
        elif asset.purchase_price < float(self.sale_proceeds):
            if book_value > 0:
                data['gain_on_disposal'] = book_value
            data['capital_gain'] = float(self.sale_proceeds) - asset.purchase_price
        # Case 3 : price > sale price
        else:
            if gain_on_disposal > 0:
                data['gain_on_disposal'] = gain_on_disposal
            else:
                data['loss_on_disposal'] = abs(gain_on_disposal)
        return data

    def calculate_journal(self):
        try:
            asset: Union[QuerySet, Asset, CalculatedDepreciation] = (
                Asset.objects.prefetch_related('calculated_depreciation_asset')
                .get(user=self.user, pk=self.asset_pk))
            # Case 1 : date == last depreciation date
            if self.get_depreciation_date() == self.get_last_depreciation_date():
                print('CASE 1')
                data = self.dispose_till_last_date(asset)
            # Case 2 : Date is more than depreciation last date so it has to calculate new depreciation
            elif self.get_depreciation_date() > self.get_last_depreciation_date():
                print('CASE 2')
                data = self.dispose_with_extra_days(asset)
            else:
                print('CASE 3')
                data = self.dispose_with_less_days(asset)
            return data
        except Asset.DoesNotExist:
            raise NotFound('Asset for this user do not exist.')


if __name__ == '__main__':
    args_one = {
        'depreciation_start_date': '2023-11-8',
        'purchase_price': 6000,
        # 'cost_limit': '',
        # 'residual_value': '',
        'averaging_method': 'FM',  # FM = full month, AD = Actual day
        'rate': 20.00,
        # 'effective_life': '',
        # 'depreciation_method': 'ST', # ST = Straight line, ND = No depreciation, 100, 150, 200,
        # FD = full depreciation
    }
    test_straight_line = StraightLine(args_one)
    result_one = test_straight_line.calculate_depreciation()
    print(result_one)  # 100.0

    args_two = {
        'depreciation_start_date': '2023-11-8',
        'purchase_price': 6000,
        'cost_limit': 3000,
        # 'residual_value': '',
        'averaging_method': 'FM',  # FM = full month, AD = Actual day
        'rate': 20.00,
        # 'effective_life': '',
        # 'depreciation_method': 'ST', # ST = Straight line, ND = No depreciation, 100, 150, 200,
        # FD = full depreciation
    }
    test_straight_line = StraightLine(args_two)
    result_one = test_straight_line.calculate_depreciation()
    print(result_one)  # 50.0
