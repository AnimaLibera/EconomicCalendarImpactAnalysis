import dataprovider as dp

provider = dp.DataProvider()
print(provider.fmp_token)

start_date = "2023-01-01"
end_date = "2023-02-01"
print(provider.economic_calendar(start_date, end_date))