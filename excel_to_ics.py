import pandas as pd
from datetime import datetime
import pytz
import re

SHEET_URL = "https://docs.google.com/spreadsheets/d/1oBx1OCvo-0nRXhghLsWzMKEUn3UsKHAUxKOx9Ram1HE/export?format=csv"

INPUT_ICS = "ffw_suschow.ics"
TEMP_ICS = "temp.ics"

berlin = pytz.timezone("Europe/Berlin")


# 🔧 Zeit umwandeln (DE → UTC)
def to_ics(date_str, time_str):
    local_dt = berlin.localize(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")


# 🔧 einfache Eingabe erkennen (z. B. "20.04 18:30 Ausbildung")
def parse_simple_input(text):
    match = re.match(r"(\d{2}\.\d{2})\s+(\d{2}:\d{2})\s+(.+)", str(text))
    if match:
        date = match.group(1)
        time = match.group(2)
        title = match.group(3)

        # Jahr automatisch setzen
        year = datetime.now().year
        date = datetime.strptime(f"{date}.{year}", "%d.%m.%Y").strftime("%Y-%m-%d")

        return date, time, title

    return None, None, None


# 📥 Sheet laden
df = pd.read_csv(SHEET_URL)

# 📥 bestehende ICS lesen
with open(INPUT_ICS, "r", encoding="utf-8") as f:
    content = f.read()

# 🔍 vorhandene UIDs sammeln (gegen Duplikate)
existing_uids = set(re.findall(r"UID:(.+)", content))

new_events = ""

for _, row in df.iterrows():

    # 🧠 einfache Eingabe prüfen
    date, time, title = parse_simple_input(row.get("Titel", ""))

    if date:
        start_time = time
        end_time = time
        summary = title
        description = ""
    else:
        date = row.get("Datum")
        start_time = row.get("Startzeit")
        end_time = row.get("Endzeit")
        summary = row.get("Titel")
        description = row.get("Beschreibung", "")

    if pd.isna(date) or pd.isna(start_time):
        continue

    dtstart = to_ics(date, start_time)
    dtend = to_ics(date, end_time if pd.notna(end_time) else start_time)

    uid = f"{dtstart}@ffw-suschow"

    # ❌ Duplikate verhindern
    if uid in existing_uids:
        continue

    event = f"""
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstart}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
END:VEVENT
"""

    new_events += event

# 🔄 nur neue Events anhängen
updated_content = content.replace("END:VCALENDAR", new_events + "\nEND:VCALENDAR")

# 💾 speichern
with open(TEMP_ICS, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("Neue Termine hinzugefügt (ohne Duplikate)")

# 🔥 Terminliste für Auswahl erzeugen
termine_liste = []

for e in updated_events:
    uid = e["uid"]

    dt = datetime.strptime(uid.split("@")[0], "%Y%m%dT%H%M%SZ")

    # UTC → deutsche Zeit
    local_dt = pytz.utc.localize(dt).astimezone(berlin)

    # Titel rausziehen
    summary = ""
    if "SUMMARY:" in e["raw"]:
        summary = e["raw"].split("SUMMARY:")[1].split("\n")[0]

    text = local_dt.strftime("%d.%m.%Y %H:%M") + " - " + summary

    termine_liste.append({
        "Anzeige": text,
        "UID": uid
    })

# CSV speichern
pd.DataFrame(termine_liste).to_csv("termine_liste.csv", index=False)

print("Terminliste erstellt")
