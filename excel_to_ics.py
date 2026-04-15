from datetime import datetime
import pandas as pd

INPUT_ICS = "ffw_suschow.ics"
EXCEL_FILE = "kalender.xlsx"
TEMP_ICS = "temp.ics"


def to_ics(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return dt.strftime("%Y%m%dT%H%M%SZ")


df = pd.read_excel(EXCEL_FILE)

with open(INPUT_ICS, "r", encoding="utf-8") as f:
    content = f.read()

events = ""

for _, row in df.iterrows():
    dtstart = to_ics(row["Datum (YYYY-MM-DD)"], row["Startzeit (HH:MM)"])
    dtend = to_ics(row["Datum (YYYY-MM-DD)"], row["Endzeit (HH:MM)"])

    uid = f"{dtstart}@ffw-suschow"

    event = f"""
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstart}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{row["Titel"]}
DESCRIPTION:{row["Beschreibung"]}
END:VEVENT
"""
    events += event

new_content = content.replace("END:VCALENDAR", events + "\nEND:VCALENDAR")

with open(TEMP_ICS, "w", encoding="utf-8") as f:
    f.write(new_content)
