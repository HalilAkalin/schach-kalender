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

# Letzten bekannten Stand einlesen (falls vorhanden)
try:
    with open("letzter_stand.txt", "r", encoding="utf-8") as datei:
        alter_stand = set(zeile.strip() for zeile in datei.readlines())
except FileNotFoundError:
    alter_stand = set()

antwort = requests.get("https://lichess.org/api/broadcast/top")
daten = antwort.json()

turniere = daten["active"]

turniere_sortiert = sorted(turniere, key=lambda t: t["tour"].get("tier", 0), reverse=True)
top_10 = turniere_sortiert[:10]

kalender = Calendar()
kalender.add("prodid", "-//Mein Schach-Kalender//")
kalender.add("version", "2.0")

verwendete_ids = set()
aktueller_stand = set()

for turnier in top_10:
    tour_id = turnier["tour"]["id"]
    name = turnier["tour"]["name"]
    start_timestamp = turnier["round"]["startsAt"]
    start_zeit = datetime.fromtimestamp(start_timestamp / 1000)

    titel = f"[Top-Turnier] {name}"

    termin = Event()
    termin.add("summary", titel)
    termin.add("dtstart", start_zeit)
    termin.add("description", f"Nächste Runde: {turnier['round']['name']}")

    kalender.add_component(termin)
    verwendete_ids.add(tour_id)
    aktueller_stand.add(titel)

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

        titel = f"{name} - {', '.join(gefundene_spieler)}"

        termin = Event()
        termin.add("summary", titel)
        termin.add("dtstart", start_zeit)
        termin.add("description", f"Nächste Runde: {turnier['round']['name']}")

        kalender.add_component(termin)
        aktueller_stand.add(titel)

for name, start_zeit in externe_turniere:
    titel = f"[Extern] {name}"

    termin = Event()
    termin.add("summary", titel)
    termin.add("dtstart", start_zeit)

    kalender.add_component(termin)
    aktueller_stand.add(titel)

with open("schach_termine.ics", "wb") as datei:
    datei.write(kalender.to_ical())

# Vergleich: was ist neu seit dem letzten Lauf?
neue_eintraege = aktueller_stand - alter_stand

if neue_eintraege:
    nachricht = "Neu: " + " | ".join(sorted(neue_eintraege))
else:
    nachricht = "Keine neuen Termine seit dem letzten Update."

with open("nachricht.txt", "w", encoding="utf-8") as datei:
    datei.write(nachricht)

# Aktuellen Stand für den nächsten Vergleich speichern (überschreibt den alten)
with open("letzter_stand.txt", "w", encoding="utf-8") as datei:
    for titel in sorted(aktueller_stand):
        datei.write(titel + "\n")

print(nachricht)