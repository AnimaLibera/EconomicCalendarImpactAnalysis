import provider as pv
import pandas as pd

class Analyst:

    def __init__(self, start_date, end_date):
        self.provider = pv.Provider()
        self.raw_economic_calendar = self.provider.economic_calendar(start_date, end_date)
        self.raw_events = self.extract_events()
        self.clean_high_impact_events = self.clean_events(self.extract_high_impact_events())
        self.raw_countrys = self.extract_countrys()
        self.unique_countrys = set(self.raw_countrys)
        self.fx_prices = self.provider.foreign_exchange_rates(start_date, end_date)

    def extract_events(self):
        """Extract Economic Calendar Events"""
        events = []
        for element in self.raw_economic_calendar:
            events.append(element["event"])
        return events
    
    def extract_high_impact_events(self):
        """Extract High Impact Events"""
        events = []
        for element in self.raw_economic_calendar:
            if element["impact"] == "High":
                events.append(element["event"])
        return events

    def clean_events(self, raw_events):
        """Clean Economic Calendar Events"""
        events = []
        for event in raw_events:
            events.append(self.clean_event(event))
        return set(events)

    def clean_event(self, event):
        """Clean Event"""
        for word in event.split():
            if self.is_parentess_word(word):
                event = event.replace(word, "").strip()
        return event
    
    def is_parentess_word(self, word):
        """Check if word is parenthesis word"""
        if word.startswith("(") and word.endswith(")"):
            return True
        else:
            return False
    
    def extract_countrys(self):
        """Extract Countries"""
        countrys = []
        for element in self.raw_economic_calendar:
            countrys.append(element["country"])
        return countrys
    
    def impact_analysis(self, country = "US", pair = "EURUSD"):
        """Build Dataframe for Impact Analysis"""

        dates = []
        records = []

        for element in self.raw_economic_calendar:
            if element["impact"] == "High" and element["country"] == country:
                datetime = pd.Timestamp(element["date"])
                event = self.clean_event(element["event"])
                expectation = element["estimate"]
                actual = element["actual"]
                deviation = self.calculate_deviation(expectation, actual)
                price_now = self.get_fx_price(datetime)

                record = [event, expectation, actual, deviation, price_now]
                dates.append(datetime)
                records.append(record)
        
        frame = pd.DataFrame(data = records, index=dates, columns=["Event", "Expectation", "Actual", "Deviation", "Price Now"])

        return frame
    
    def calculate_deviation(self, expectation, actual):
        """Calculate Deviation"""
        if actual == None or expectation == None:
            return None
        elif expectation == 0:
            return expectation
        return (actual - expectation) / expectation
    
    def get_fx_price(self, datetime):
        """Get Foreign Exchange Price"""

        if datetime in self.fx_prices.index:
            return self.fx_prices[datetime]
        else:
            return None