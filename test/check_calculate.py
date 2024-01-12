

def calculate_depreciation(purchase_price, residual_value, rate, effective_life, days_in_year, number_of_days_in_month):
    result = 0.00
    cost_limit = purchase_price
    if rate:
        result = ((cost_limit - residual_value) * rate) / (100 * days_in_year)
    elif effective_life:
        result = ((cost_limit - residual_value) / effective_life) / (days_in_year * number_of_days_in_month)
    return round(result, 2)


def calculate_depreciation_2(purchase_price, residual_value, rate, effective_life, days_in_year, number_of_days_in_month):
    result = 0.00
    cost_limit = purchase_price
    declining_balance = 1.0  # Assuming no multiplier for simplicity
    if rate:
        result = ((cost_limit - residual_value) * rate) / (100 * days_in_year) * declining_balance
    elif effective_life:
        result = ((cost_limit - residual_value) / effective_life) / (days_in_year * number_of_days_in_month) * declining_balance
    return round(result, 2)


if __name__ == '__main__':
    # Simulation with varying rate
    rate_values = [5, 10, 15, 20, 25]
    for rate in rate_values:
        result_depreciation = calculate_depreciation(
            purchase_price=1000,
            residual_value=200,
            rate=rate,
            effective_life=5,
            days_in_year=365,
            number_of_days_in_month=30
        )
        result_depreciation_2 = calculate_depreciation_2(
            purchase_price=1000,
            residual_value=200,
            rate=rate,
            effective_life=5,
            days_in_year=365,
            number_of_days_in_month=30
        )
        print(f"Rate: {rate}, Result (calculate_depreciation): {result_depreciation}, Result (calculate_depreciation_2): {result_depreciation_2}")

    # Simulation with varying effective_life
    effective_life_values = [3, 5, 7, 10, 15]
    for effective_life in effective_life_values:
        result_depreciation = calculate_depreciation(
            purchase_price=1000,
            residual_value=200,
            rate=10,
            effective_life=effective_life,
            days_in_year=365,
            number_of_days_in_month=30
        )
        result_depreciation_2 = calculate_depreciation_2(
            purchase_price=1000,
            residual_value=200,
            rate=10,
            effective_life=effective_life,
            days_in_year=365,
            number_of_days_in_month=30
        )
        print(f"Effective Life: {effective_life}, Result (calculate_depreciation): {result_depreciation}, Result (calculate_depreciation_2): {result_depreciation_2}")
