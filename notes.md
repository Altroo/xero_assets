# ! Formulas :
# * Straight line (ST)
# ? Case 1 (Rate):
# purchase_price * rate / 100 = result
# ? Case 2 (Effective_life):
# 100% / effective_life = result in %
# purchase_price * result in % = new result
# * Declining balance (100)
# ? Case 1 (Rate):
# year one result = (purchase_price * rate / 100)
# year two result = (purchase_price - year one result) = result, (result * rate / 100)
# year three result = (result - year two result) = result 2, (result 2 * rate / 100)
# * Declining balance (150)
# ? Case 1 (Effective_life):
# result in % = declaning_balance (150%) / effective_life
# year one result = (purchase_price * result in %)
# year two result = (purchase_price - year one result) = result, (result * result in %)
# year three result = (result - year two result) = result 2, (result 2 * result in %)
# * Full Depreciation (FD)
# ? Case 1 (Rate):
# TODO Missing
# 1300 - 1300 = 0
# ? Case 2 (Effective_life):
# TODO Missing
# * With residual value
# purchase_price - residual value = result
# * With cost limit
# TODO Missing
# * Averaging Method Actual Days (AD)
# Examples :
# Annual depreciation = 260
# daily depreciation = annual depreciation / 365 days
# result = daily depreciation * number of days
# * Averagin Method Full Month (FM)
# Annual depreciation 260
# monthly depreciation = annual depreciation / 12
# depreciation of each month = monthly depreciation / 12 months


