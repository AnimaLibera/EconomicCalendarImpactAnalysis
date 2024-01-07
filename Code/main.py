import provider as pd
import analyst as al
import json

start_date = "2023-01-01"
end_date = "2023-02-01"
#provider = pd.Provider()
#print(provider.fmp_token)
#json_data = provider.economic_calendar(start_date, end_date)
#print(json.dumps(json_data, indent=2))
analyst = al.Analyst(start_date, end_date)
for event in analyst.clean_events():
    print(event)
