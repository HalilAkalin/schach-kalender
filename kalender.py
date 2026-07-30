import requests
from datetime import datetime
from icalendar import Calendar, Event

TESTMODUS = False

with open("spieler.txt", "r", encoding="utf-8") as datei:
    spieler_liste = [zeile.strip() for zeile in datei.readlines()]

with open("turniere.txt", "r", encoding="utf-8") as datei:
    externe_turniere = []
    for zeile in datei.readlines():
        zeile = zeile.strip()
        if zeile:
            teile = zeile.split(";")
            name = teile[0]
            datum = teile[1]
            uhrzeit = teile[2]
            start_zeit = datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
            externe_turniere.append((name, start_zeit))

antwort = requests.get("https://lichess.org/api/broadcast/top")
daten = antwort.json()

turniere = daten["active"]

turniere_sortiert = sorted(turniere, key=lambda t: t["tour"].get("tier", 0), reverse=True)
top_10 = turniere_sortiert[:10]

kalender = Calendar()
kalender.add("prodid", "-//Mein Schach-Kalender//")
kalender.add("version", "2.0")

verwendete_ids = set()
anzahl_treffer = 0
anzahl_top = 0

for turnier in top_10:
    tour_id = turnier["tour"]["id"]
    name = turnier["tour"]["name"]
    start_timestamp = turnier["round"]["startsAt"]
    start_zeit = datetime.fromtimestamp(start_timestamp / 1000)

    termin = Event()
    termin.add("summary", f"[Top-Turnier] {name}")
    termin.add("dtstart", start_zeit)
    termin.add("description", f"Nächste Runde: {turnier['round']['name']}")

    kalender.add_component(termin)
    verwendete_ids.add(tour_id)
    anzahl_top += 1

for turnier in turniere:
    tour_id = turnier["tour"]["id"]

    if tour_id in verwendete_ids:
        continue

    spieler_text = turnier["tour"]["info"].get("players", "")
    gefundene_spieler = [s for s in spieler_liste if s.split()[-1] in spieler_text]

    if gefundene_spieler:
        name = turnier["tour"]["name"]
        start_timestamp = turnier["round"]["startsAt"]
        start_zeit = datetime.fromtimestamp(start_timestamp / 1000)

        termin = Event()
        termin.add("summary", f"{name} - {', '.join(gefundene_spieler)}")
        termin.add("dtstart", start_zeit)
        termin.add("description", f"Nächste Runde: {turnier['round']['name']}")

        kalender.add_component(termin)
        anzahl_treffer += 1

anzahl_extern = 0
for name, start_zeit in externe_turniere:
    termin = Event()
    termin.add("summary", f"[Extern] {name}")
    termin.add("dtstart", start_zeit)

    kalender.add_component(termin)
    anzahl_extern += 1

with open("schach_termine.ics", "wb") as datei:
    datei.write(kalender.to_ical())

print(f"Fertig! {anzahl_top} Top-Turnier(e), {anzahl_treffer} Spieler-Treffer und {anzahl_extern} externe Turniere in schach_termine.ics gespeichert.")