import requests
from datetime import datetime
from icalendar import Calendar, Event

# Testmodus: True = ausführliche Debug-Ausgaben, False = nur das Wichtigste
TESTMODUS = False

def log_schreiben(nachricht):
    zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("verlauf.log", "a", encoding="utf-8") as logdatei:
        logdatei.write(f"{zeitstempel} - {nachricht}\n")

try:
    with open("spieler.txt", "r", encoding="utf-8") as datei:
        spieler_liste = [zeile.strip() for zeile in datei.readlines()]

    if TESTMODUS:
        print("Eingelesene Spieler:", spieler_liste)
        print()

    antwort = requests.get("https://lichess.org/api/broadcast/top")
    daten = antwort.json()

    turniere = daten["active"]

    turniere_sortiert = sorted(turniere, key=lambda t: t["tour"].get("tier", 0), reverse=True)
    top_10 = turniere_sortiert[:10]

    if TESTMODUS:
        print("=== Top 10 Turniere ===\n")
        for turnier in top_10:
            name = turnier["tour"]["name"]
            tier = turnier["tour"].get("tier", "-")
            naechste_runde = turnier["round"]["name"]
            start_timestamp = turnier["round"]["startsAt"]
            start_zeit = datetime.fromtimestamp(start_timestamp / 1000)
            gelistete_spieler = turnier["tour"]["info"].get("players", "keine gelistet")

            print(f"{name} (Tier {tier})")
            print(f"  Nächste Runde: {naechste_runde} - startet am {start_zeit}")
            print(f"  Gelistete Spieler: {gelistete_spieler}")
            print()

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

        if TESTMODUS:
            print(f"Top-Turnier: {name} - startet am {start_zeit}")

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

            if TESTMODUS:
                print(f"Treffer: {name}")
                print(f"  Gefundene Spieler: {', '.join(gefundene_spieler)}")
                print(f"  Nächste Runde startet am {start_zeit}")
                print()

    with open("schach_termine.ics", "wb") as datei:
        datei.write(kalender.to_ical())

    ergebnis = f"Erfolgreich - {anzahl_top} Top-Turnier(e) und {anzahl_treffer} Spieler-Treffer"
    print(f"Fertig! {anzahl_top} Top-Turnier(e) und {anzahl_treffer} Spieler-Treffer in schach_termine.ics gespeichert.")
    log_schreiben(ergebnis)

except Exception as fehler:
    log_schreiben(f"Fehler - {fehler}")
    print(f"Es ist ein Fehler aufgetreten: {fehler}")