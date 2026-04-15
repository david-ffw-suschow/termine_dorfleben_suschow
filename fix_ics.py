from datetime import datetime
import re

INPUT_FILE = "temp.ics"
OUTPUT_FILE = "ffw_suschow.ics"


def parse_event(block):
    dtstart = re.search(r"DTSTART:(\d+T\d+Z)", block)
    return {
        "raw": block,
        "dtstart": dtstart.group(1) if dtstart else None
    }


def fix_uid(block, dtstart):
    return re.sub(r"UID:.*", f"UID:{dtstart}@ffw-suschow", block)


def parse_dt(dt):
    return datetime.strptime(dt, "%Y%m%dT%H%M%SZ")


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

header = content.split("BEGIN:VEVENT")[0]
events_raw = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", content, re.DOTALL)

events = []

for block in events_raw:
    event = parse_event(block)
    if event["dtstart"]:
        fixed = fix_uid(block, event["dtstart"])
        events.append((parse_dt(event["dtstart"]), fixed))

events.sort(key=lambda x: x[0])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(header)
    for _, e in events:
        f.write(e + "\n")
    f.write("END:VCALENDAR\n")
