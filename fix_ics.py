from datetime import datetime
import re

INPUT_FILE = "input.ics"
OUTPUT_FILE = "output_fixed.ics"


def parse_event(block):
    """Extrahiert wichtige Felder aus einem VEVENT"""
    dtstart_match = re.search(r"DTSTART:(\d+T\d+Z)", block)
    uid_match = re.search(r"UID:(.+)", block)

    dtstart = dtstart_match.group(1) if dtstart_match else None
    uid = uid_match.group(1) if uid_match else None

    return {
        "raw": block,
        "dtstart": dtstart,
        "uid": uid
    }


def fix_uid(event):
    """Setzt UID = DTSTART für Konsistenz"""
    if event["dtstart"]:
        new_uid = f"{event['dtstart']}@ffw-suschow"
        event["raw"] = re.sub(r"UID:.*", f"UID:{new_uid}", event["raw"])
    return event


def parse_datetime(dt):
    return datetime.strptime(dt, "%Y%m%dT%H%M%SZ")


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Header & Footer trennen
    header = content.split("BEGIN:VEVENT")[0]
    events_raw = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", content, re.DOTALL)

    events = []

    for block in events_raw:
        event = parse_event(block)

        # nur valide Events berücksichtigen
        if event["dtstart"]:
            event = fix_uid(event)
            events.append(event)

    # 🔥 Sortieren nach DTSTART
    events.sort(key=lambda e: parse_datetime(e["dtstart"]))

    # 🔥 Neu zusammensetzen
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)

        for event in events:
            f.write(event["raw"] + "\n")

        f.write("END:VCALENDAR\n")

    print("Fertig! Datei gespeichert als:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
