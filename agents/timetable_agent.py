import pandas as pd
from datetime import datetime

class TimetableAgent:
    description = "Handles timetable queries."

    def __init__(self, csv_path="c:/workspace/mwtuni/data/lukkari.csv"):
        """
        Initializes the TimetableAgent by loading and preparing timetable data from a CSV file.
        """
        try:
            # Load the CSV file with the specified encoding and delimiter
            self.df = pd.read_csv(csv_path, delimiter=";", encoding="utf-8")
            self.df.columns = [col.strip() for col in self.df.columns]  # Clean up column names

            # Rename columns if necessary to standardize access
            expected_columns = {
                "Viikko": "Week", "Päivä": "Day", "Pvm": "Pvm", 
                "Aika": "Aika", "Kurssi": "Kurssi", "Tila": "Tila", 
                "Tiimi": "Team", "Opettaja": "Teacher"
            }
            self.df.rename(columns=expected_columns, inplace=True)

        except Exception as e:
            print(f"Error loading timetable CSV: {e}")
            self.df = None

    def get_next_class(self):
        """
        Returns information about the next upcoming class including date, time, course, and location.
        """
        if self.df is None:
            return "Timetable data is not available."

        try:
            # Ensure required columns are present in the data
            necessary_columns = ["Pvm", "Aika", "Kurssi", "Tila"]
            if not all(col in self.df.columns for col in necessary_columns):
                return "The timetable data is missing required columns."

            # Drop rows with missing values in essential columns
            self.df = self.df[necessary_columns].dropna(subset=necessary_columns)

            # Convert the "Pvm" column to datetime format
            self.df["Pvm"] = pd.to_datetime(self.df["Pvm"], errors="coerce", dayfirst=True)
            now = datetime.now()

            # Filter for upcoming classes based on the current date and time
            upcoming_classes = self.df[self.df["Pvm"] >= now].sort_values(by=["Pvm", "Aika"]).head(1)

            # Check if any upcoming class was found
            if upcoming_classes.empty:
                return "No upcoming classes were found in the timetable."

            # Extract the details of the next class
            next_class = upcoming_classes.iloc[0]
            return (f"Seuraava luento: {next_class['Kurssi']} {next_class['Pvm'].strftime('%d.%m.%Y')} "
                    f"klo {next_class['Aika']} tilassa {next_class['Tila']}.")
        
        except KeyError as e:
            return f"Error: Required column missing - {e}"
        except Exception as e:
            return f"Error processing timetable data: {str(e)}"
