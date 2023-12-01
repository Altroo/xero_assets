from typing import Union, Literal, List, Dict, Any
from datetime import date, datetime, timedelta
from calendar import isleap, monthrange


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
        year: List[str] = self.start_date.split('-')
        return 365 + isleap(int(year[0]))

    def number_of_days_in_month(self) -> int:
        date_object: date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        last_month_day: int = monthrange(date_object.year, date_object.month)[1]
        last_date: date = date(date_object.year, date_object.month, last_month_day)
        delta: timedelta = last_date - date_object
        return delta.days


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
                    result: Union[int, float] = (((self.purchase_price / self.effective_life) / self.days_in_year()) *
                                                 self.number_of_days_in_month())
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


# if __name__ == '__main__':
#     args_one = {
#         'depreciation_start_date': '8/11/2023',
#         'purchase_price': 6000,
#         # 'cost_limit': '',
#         # 'residual_value': '',
#         'averaging_method': 'FM',  # FM = full month, AD = Actual day
#         'rate': 20.00,
#         # 'effective_life': '',
#         # 'depreciation_method': 'ST', # ST = Straight line, ND = No depreciation, 100, 150, 200, FD = full depreciation
#     }
#     test_straight_line = StraightLine(args_one)
#     result_one = test_straight_line.calculate_depreciation()
#     print(result_one)  # 100.0
#
#     args_two = {
#         'depreciation_start_date': '8/11/2023',
#         'purchase_price': 6000,
#         'cost_limit': 3000,
#         # 'residual_value': '',
#         'averaging_method': 'FM',  # FM = full month, AD = Actual day
#         'rate': 20.00,
#         # 'effective_life': '',
#         # 'depreciation_method': 'ST', # ST = Straight line, ND = No depreciation, 100, 150, 200, FD = full depreciation
#     }
#     test_straight_line = StraightLine(args_two)
#     result_one = test_straight_line.calculate_depreciation()
#     print(result_one)  # 50.0
