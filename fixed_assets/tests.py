from typing import Union
import pytest
from datetime import date, datetime
import calendar


class Init:
    purchase_price: int = 6000
    purchase_date: str = '8/11/2023'
    rate: float = 20.00

    def days_in_year(self) -> int:
        year = self.purchase_date.split('/')
        return 365 + calendar.isleap(int(year[2]))


# ! Full month = devided by 12 months no need to calculate remaining days
class TestStraightLineFullMonthRate(Init):
    def test_rate_full_month(self):
        # Equation
        # (Purchase price * rate) / 12
        result: Union[int, float] = ((self.purchase_price * self.rate) / 100) / 12
        print('\nResult should be 100')
        # depreciation of 100 for month 11
        assert round(result, 2) == 100

    def test_rate_full_month_cost_limit(self):
        # Equation
        # (Cost Limit * rate) / 12
        cost_limit: int = 3000
        # ! Cost limit if available it's used instead of "purchase_price"
        result: Union[int, float] = ((cost_limit * self.rate) / 100) / 12
        print('\nResult should be 50')
        # depreciation of 50 for month 11
        assert result == 50

    def test_rate_full_month_residual_value(self):
        residual_value: int = 1500
        # ! Residual value is subtracted from the purchase price
        # Equation
        # ((Purchase price ‐ Residual Value) * rate)/12
        result: Union[int, float] = (((self.purchase_price - residual_value) * self.rate / 100) / 12)
        print('\nResult should be 75')
        assert result == 75

    def test_rate_full_month_cost_limit_residual_value(self):
        residual_value: int = 600
        cost_limit: int = 4500
        # ! Cost limit if available it's used instead of "purchase_price" then substract residual value
        # Equation
        # ((Cost Limit ‐ Residual Value) * rate) / 12
        result: Union[int, float] = (((cost_limit - residual_value) * self.rate / 100) / 12)
        print('\nResult should be 65')
        assert result == 65


# ! Actual days = Devides by the remaining days from the depreciation date to the last day of the month
class TestStaightLineActualDaysRate(Init):
    def test_rate_actual_days_effective_year(self):
        # Equation
        # ((Purchase price * rate)/ year days) * number of days
        # ((6000*0.20)/365) * 22
        date_object = datetime.strptime(self.purchase_date, '%d/%m/%Y').date()
        last_month_day = calendar.monthrange(2023, 11)[1]
        last_date = date(2023, 11, last_month_day)
        delta = last_date - date_object
        result: Union[int, float] = (self.purchase_price * (self.rate / 100) / self.days_in_year()) * delta.days
        assert round(result, 2) == 72.33

    def test_cost_limit_actual_days_effective_year(self):
        # Equation
        # ((Cost Limit / Effective Life)/ year days) * number of days
        # ((3000/5)/365) * 22
        cost_limit = 3000
        effective_year = 5
        date_object = datetime.strptime(self.purchase_date, '%d/%m/%Y').date()
        last_month_day = calendar.monthrange(2023, 11)[1]
        last_date = date(2023, 11, last_month_day)
        delta = last_date - date_object
        result: Union[int, float] = ((cost_limit / effective_year) / self.days_in_year()) * delta.days
        assert round(result, 2) == 36.16

    def test_residual_value_actual_days_effective_year(self):
        # Equation
        # (((Purchase Price - Residual Value) / Effective Life)/ year days) * number of days
        # (((6000-1500)/5)/365) *22
        residual_value = 1500
        effective_year = 5
        date_object = datetime.strptime(self.purchase_date, '%d/%m/%Y').date()
        last_month_day = calendar.monthrange(2023, 11)[1]
        last_date = date(2023, 11, last_month_day)
        delta = last_date - date_object
        result: Union[int, float] = ((((self.purchase_price - residual_value) / effective_year) / self.days_in_year()) *
                                     delta.days)
        assert round(result, 2) == 54.25

    def test_cost_limit_residual_value_actual_days_effective_year(self):
        # Equation
        # (((Cost Limit- Residual Value) / Effective Life)/ year days) * number of days
        # (((4500-600)/5)/365) *22
        residual_value = 600
        cost_limit = 4500
        effective_year = 5
        date_object = datetime.strptime(self.purchase_date, '%d/%m/%Y').date()
        last_month_day = calendar.monthrange(2023, 11)[1]
        last_date = date(2023, 11, last_month_day)
        delta = last_date - date_object
        result: Union[int, float] = ((((cost_limit - residual_value) / effective_year) / self.days_in_year()) *
                                     delta.days)
        assert round(result, 2) == 47.01
