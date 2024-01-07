import provider as pd
import json

provider = pd.Provider()
print(provider.fmp_token)

start_date = "2023-01-01"
end_date = "2023-02-01"
json_data = provider.economic_calendar(start_date, end_date)
print(json.dumps(json_data, indent=2))