import provider as pd
import analyst as al
import json

start_date = "2024-01-01"
end_date = "2024-01-07"
#provider = pd.Provider()
#fx_prices = provider.foreign_exchange_rates(start_date, end_date)
#print(fx_prices)
#print(fx_prices.info())

#print(provider.fmp_token)
#json_data = provider.economic_calendar(start_date, end_date)
#print(json.dumps(json_data, indent=2))
analyst = al.Analyst(start_date, end_date)
frame = analyst.impact_analysis()
print(frame)
#for event in analyst.clean_high_impact_events:
#    print(event)
#for country in analyst.unique_countrys:
#    print(country)