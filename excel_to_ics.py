import pandas as pd
from datetime import datetime

SHEET_URL = "https://docs.google.com/spreadsheets/d/1oBx1OCvo-0nRXhghLsWzMKEUn3UsKHAUxKOx9Ram1HE/export?format=csv"

INPUT_ICS = "ffw_suschow.ics"
TEMP_ICS = "temp.ics"


from datetime import datetime
import pytz

berlin = pytz.timezone("Europe/Berlin")


def to_ics(date, time):
    local_dt = berlin.localize(datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S"))
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")


df = pd.read_csv(SHEET_URL)

with open(INPUT_ICS, "r", encoding="utf-8") as f:
    content = f.read()

events = ""

for _, row in df.iterrows():
    dtstart = to_ics(row["Datum"], row["Startzeit"])
    dtend = to_ics(row["Datum"], row["Endzeit"])

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
