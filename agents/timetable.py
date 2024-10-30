import pandas as pd
from datetime import datetime

class TimetableAgent:
    def __init__(self, csv_path="lukkari.csv"):
        try:
            self.df = pd.read_csv(csv_path, delimiter=";", encoding="latin1")
            self.df.columns = [col.strip() for col in self.df.columns]  # Puhdistetaan sarakenimet
        except Exception as e:
            print(f"Error loading timetable CSV: {e}")
            self.df = None

    def get_next_class(self):
        """Palauttaa seuraavan tulevan luennon päivämäärän, ajan, kurssin ja luokan perusteella."""
        if self.df is None:
            return "Lukujärjestysdataa ei ole saatavilla."

        # Suodatetaan nykyisestä päivämäärästä eteenpäin
        now = datetime.now()
        self.df["Pvm"] = pd.to_datetime(self.df["Pvm"], errors="coerce", dayfirst=True)
        upcoming_classes = self.df[self.df["Pvm"] >= now].sort_values(by=["Pvm", "Aika"]).head(1)

        if upcoming_classes.empty:
            return "Seuraavia luentoja ei löytynyt lukujärjestyksestä."

        next_class = upcoming_classes.iloc[0]
        return f"Seuraava luento: {next_class['Kurssi']} {next_class['Pvm'].strftime('%d.%m.%Y')} klo {next_class['Aika']} luokassa {next_class['Tila']}."
