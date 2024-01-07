import provider as pv
import pandas as pd

class Analyst:

    def __init__(self, start_date, end_date):
        self.raw_economic_calendar = pv.Provider().economic_calendar(start_date, end_date)
        self.raw_events = self.extract_events()
        self.clean_high_impact_events = self.clean_events(self.extract_high_impact_events())
        self.raw_countrys = self.extract_countrys()
        self.unique_countrys = set(self.raw_countrys)

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
                event = event.replace(word, "")
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
                record = [event, expectation, actual, deviation]
                dates.append(datetime)
                records.append(record)
        
        frame = pd.DataFrame(data = records, index=dates, columns=["Event", "Expectation", "Actual", "Deviation"])

        return frame
    
    def calculate_deviation(self, expectation, actual):
        """Calculate Deviation"""
        if actual == None or expectation == None:
            return None
        return (actual - expectation) / expectation