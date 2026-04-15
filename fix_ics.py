from datetime import datetime
import re

INPUT_FILE = "input.ics"
OUTPUT_FILE = "output.ics"


def parse_event(block):
    dtstart_match = re.search(r"DTSTART:(\d+T\d+Z)", block)
    return {
        "raw": block,
        "dtstart": dtstart_match.group(1) if dtstart_match else None
    }


def fix_uid(block, dtstart):
    new_uid = f"{dtstart}@ffw-suschow"
    if "UID:" in block:
        block = re.sub(r"UID:.*", f"UID:{new_uid}", block)
    else:
        block = block.replace("BEGIN:VEVENT", f"BEGIN:VEVENT\nUID:{new_uid}")
    return block


def parse_datetime(dt):
    return datetime.strptime(dt, "%Y%m%dT%H%M%SZ")


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

header = content.split("BEGIN:VEVENT")[0]
events_raw = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", content, re.DOTALL)

events = []

for block in events_raw:
    event = parse_event(block)

    if event["dtstart"]:
        fixed_block = fix_uid(block, event["dtstart"])
        events.append((parse_datetime(event["dtstart"]), fixed_block))

# 🔥 Sortieren
events.sort(key=lambda x: x[0])

# 🔥 Schreiben
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(header)

    for _, event in events:
        f.write(event + "\n")

    f.write("END:VCALENDAR\n")

print("Kalender erfolgreich korrigiert!")
