import pandas as pd
from datetime import datetime

class TimetableAgent:
    def __init__(self, csv_path="c:/workspace/mwtuni/data/lukkari.csv"):
        try:
            # Ladataan CSV-tiedosto ilman ylimääräisiä rivejä
            self.df = pd.read_csv(csv_path, delimiter=";", encoding="latin1")
            self.df.columns = [col.strip() for col in self.df.columns]  # Puhdistetaan sarakenimet
            print("Loaded columns:", self.df.columns)  # Tulostetaan sarakenimet tarkistusta varten

            # Uudelleennimetään sarakkeet, jos niissä on erikoismerkkejä
            expected_columns = {"Viikko": "Week", "Päivä": "Day", "Pvm": "Pvm", "Aika": "Aika", 
                                "Kurssi": "Kurssi", "Tila": "Tila", "Tiimi": "Team", "Opettaja": "Teacher"}
            self.df.rename(columns=expected_columns, inplace=True)

        except Exception as e:
            print(f"Error loading timetable CSV: {e}")
            self.df = None

    def get_next_class(self):
        """Palauttaa seuraavan tulevan luennon päivämäärän, ajan, kurssin ja luokan perusteella."""
        if self.df is None:
            return "Lukujärjestysdataa ei ole saatavilla."

        try:
            # Varmistetaan, että vaaditut sarakkeet ovat olemassa
            necessary_columns = ["Pvm", "Aika", "Kurssi", "Tila"]
            if not all(col in self.df.columns for col in necessary_columns):
                return "Lukujärjestysdatasta puuttuu tarvittavia sarakkeita."

            self.df = self.df[necessary_columns].dropna(subset=["Pvm", "Aika", "Kurssi", "Tila"])

            # Muunnetaan "Pvm" sarake datetime-muotoon ja käsitellään virheet
            self.df["Pvm"] = pd.to_datetime(self.df["Pvm"], errors="coerce", dayfirst=True)
            now = datetime.now()

            # Suodatetaan vain tulevat luennot nykyhetkestä alkaen
            upcoming_classes = self.df[self.df["Pvm"] >= now].sort_values(by=["Pvm", "Aika"]).head(1)

            if upcoming_classes.empty:
                return "Seuraavia luentoja ei löytynyt lukujärjestyksestä."

            # Muotoillaan vastaus tulevasta luennosta
            next_class = upcoming_classes.iloc[0]
            return f"Seuraava luento: {next_class['Kurssi']} {next_class['Pvm'].strftime('%d.%m.%Y')} klo {next_class['Aika']} luokassa {next_class['Tila']}."
        
        except KeyError as e:
            return f"Error: Required column missing - {e}"
        except Exception as e:
            return f"Error processing timetable data: {str(e)}"
