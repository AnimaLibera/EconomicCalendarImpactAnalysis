import provider as pd

class Analyst:

    def __init__(self, start_date, end_date):
        self.raw_economic_calendar = pd.Provider().economic_calendar(start_date, end_date)
        self.raw_events = self.extract_events()

    def extract_events(self):
        """Extract Economic Calendar Events"""
        events = []
        for event in self.raw_economic_calendar:
            events.append(event["event"])
        return events
    
    def clean_events(self):
        """Clean Economic Calendar Events"""
        events = []
        for event in self.raw_events:
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
    