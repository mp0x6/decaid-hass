# Decaid für Home Assistant

Custom Integration für die lokale API der **Decent Espresso Decaid-App**.
Version 0.1.0; Home Assistant ab 2025.12.0. Dies ist eine eigenständige,
informelle Integration, kein offizielles Decent-Produkt und kein Supervisor-Add-on.
Die Decaid-App läuft weiterhin auf dem Tablet und übernimmt die Geräteverbindung.

## Installation

1. Aus diesem Paket den Ordner `custom_components/decaid` nach
   `/config/custom_components/decaid` auf deinem Home-Assistant-System kopieren.
2. Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen → Decaid**.
4. Die Adresse der laufenden App angeben, beispielsweise
   `http://192.168.1.42:8080`. Home Assistant muss das Tablet erreichen können.
   Der normale lokale Gerätezugriff benötigt in der referenzierten API keinen Token.
   Optional kann ein von Decaid ausgestellter API-Client-Token eingetragen werden,
   etwa für den Account-Proxy. Seine Berechtigungen werden durch Decaid geprüft.
5. Die Integration erstellt ein Decaid-Gerät. Ein laufender Bezug, Dampf und
   Heißwasser lassen sich über zunächst deaktivierte Button-Entitäten aktivieren.
   Diese bei Bedarf in der Entitätenverwaltung freischalten.

Es ist keine MQTT-Bridge erforderlich. Bei geänderter Tablet-Adresse die Integration
über **Neu konfigurieren** aktualisieren. Die Optionen erlauben 10–300 Sekunden
für die ergänzenden REST-Abfragen (Standard: 30 Sekunden) sowie rohe Stream-Ereignisse.

### HACS

In HACS unter **Benutzerdefinierte Repositories** die URL
`https://github.com/mp0x6/decaid-hass` hinzufügen und **Integration** auswählen.
Anschließend Decaid herunterladen, Home Assistant neu starten und die Integration
wie oben beschrieben einrichten. Das Repository ist nicht im HACS-Standardkatalog.

## Direkte Entitäten

| Bereich | Funktionen |
|---|---|
| Maschine | Zustand, Unterzustand, Druck/Solldruck, Durchfluss/Solldurchfluss, Misch-, Gruppen- und Dampftemperatur, Solltemperaturen, Profilschritt |
| Waage | Gewicht, gravimetrischer Durchfluss, Batterie, Timer; Tara und Timer-Start/-Stopp/-Reset |
| Wasser | Tankfüllhöhe und Nachfüllgrenze in mm; Wassermangel |
| Bezug | Phase, momentaner Entscheidungsgrund, Waagenverbindung und Waagenverlust |
| Rezept | Profilwahl, Kaffee, Mühle, Dosis und Zielgewicht; Dampf-, Heißwasser- und Spülparameter |
| Steuerung | Wach/Schlaf-Schalter, Wake/Stop, Espresso, Dampf, Heißwasser, Spülen, Steam-Rinse und Schritt überspringen |
| Tablet | Helligkeit, Wake-Lock, aktive Helligkeitsbegrenzung bei niedrigem Akku |
| Zusatzfunktionen | USB-Laden; Bengle-Tassenwärmer (standardmäßig deaktiviert, bei anderen Maschinen nicht verfügbar) |

„Ready“ bedeutet hier **Maschinenzustand idle**, keine zusätzliche Garantie einer
vollständig thermisch stabilisierten Brühgruppe. Der Schalter „Machine awake“ ist
kein Netzschalter: Einschalten fordert `idle` an und kann damit auch einen laufenden
Bezug stoppen. Dafür gibt es ebenfalls die ausdrücklich benannte Taste „Wake / stop“.

Zielgewicht 0 schaltet Stop-at-weight gemäß Decaid aus. Die Temperatur-Entität
für Dampf bietet den gemeinsamen eingeschalteten Bereich 135–160 °C an.
Dampfheizung aus (`0`) oder Bengle bis 165 °C sind per Workflow-Aktion möglich.
Die Zahlenbereiche der übrigen Entitäten sind konservative UI-Bereiche, keine
vollständige Gerätevalidierung. Decaid entscheidet über unterstützte Werte.
Profilbezeichnungen enthalten die stabile Profil-ID, damit gleiche Titel eindeutig bleiben.

## API-Abdeckung

Basis: [`rest_v1.yml`](https://github.com/decentespresso/decaid/blob/a6e2a0594c8a3cd96c58a75279d2b8a2f29a1651/assets/api/rest_v1.yml)
und [`websocket_v1.yml`](https://github.com/decentespresso/decaid/blob/a6e2a0594c8a3cd96c58a75279d2b8a2f29a1651/assets/api/websocket_v1.yml),
Commit `a6e2a0594c8a3cd96c58a75279d2b8a2f29a1651`.

**152 von 153 dokumentierten REST-Operationen sind durch eine allgemeine Aktion
adressierbar**, zusätzlich zu den Entitäten. Das ist Transport-Abdeckung; die
Integration besitzt nicht für jeden Endpunkt ein eigenes Formular oder eine
lokale vollständige Payload-Validierung. Funktionen, die einen bestimmten
Maschinentyp, Debug-Build, Account, Token oder eine Zustimmung in Decaid benötigen,
behalten diese Voraussetzungen.

Alle **14 WebSocket-Kanaltypen** können abonniert werden. Sieben Kernkanäle
werden automatisch verbunden. Zusätzliche Sensoren, Waagen, Plugins, Rohdaten,
Logs und Updates sind über parametrisierte Abonnements und Ereignisse erreichbar.
Bidirektionale Nachrichten werden unverändert weitergegeben; erlaubte Befehle
und Bestätigungen definiert die Decaid-AsyncAPI. Es gibt keine automatische
Zuordnung einer Antwort zu einem Befehl.

Die vollständige Endpunktliste steht in [docs/API_COVERAGE.md](docs/API_COVERAGE.md).
Beans, Batches, Grinder, Shot-/Steam-Historie, Profile-CRUD, Plugin-/Skin-Verwaltung,
Gerätesuche, Kalibrierung, Firmware, Zeitpläne, Präsenz, Import/Export, Account-Proxy
und Debug-Funktionen sind damit über Aktionen erreichbar.

### Grenzen

- `POST /api/v1/derek/answers/stream` (Derek-Chat/SSE) wird bewusst nicht unterstützt.
- Antworten sind auf 8 MiB und REST-Anfragen auf 45 Sekunden begrenzt. Große Exporte
  und lange Firmware-/Import-Vorgänge direkt in Decaid ausführen. Ein Timeout
  bedeutet nicht, dass eine bereits gestartete Aktion auf dem Gerät abgebrochen wurde.
- Multipart-Uploads benötigen einen vom Aufrufer korrekt aufgebauten Base64-Body
  einschließlich Boundary im Content-Type. Es gibt keinen HA-Dateiauswahldialog.
- Zusätzliche WebSocket-Abonnements gelten bis zum Neuladen/Neustart. Bei Bedarf
  mit einer Home-Assistant-Startautomation erneut abonnieren.
- Kein historischer Import ins HA-Recorder-System; Shot-Historie wird nur auf
  ausdrücklichen API-Aufruf gelesen. Live-Telemetrie folgt den normalen HA-Regeln.
- Nicht an echter Decent-Hardware getestet. Die Tests benutzen einen lokalen
  HTTP-/WebSocket-Testserver und die echte Home-Assistant-Installation 2025.12.5.

## Aktionen und Automationen

Alle Aktionen verwenden `entry_id` zur eindeutigen Auswahl, auch bei mehreren
Tablets. Im visuellen Aktionseditor wird die Integration ausgewählt. Die zugehörige
ID kann für YAML aus diesem Editor übernommen werden; `DEINE_ENTRY_ID` ist ein Platzhalter.

### Aufwecken

```yaml
action: decaid.set_state
data:
  entry_id: DEINE_ENTRY_ID
  state: idle
```

### Rezept ändern

Es werden nur die angegebenen Felder geändert. Decaid führt den Deep-Merge aus.

```yaml
action: decaid.set_workflow
data:
  entry_id: DEINE_ENTRY_ID
  workflow:
    context:
      targetDoseWeight: 18
      targetYield: 36
    steamSettings:
      targetTemperature: 150
```

### Historie oder beliebigen REST-Endpunkt lesen

```yaml
action: decaid.api_request
data:
  entry_id: DEINE_ENTRY_ID
  method: GET
  path: /api/v1/shots/latest
response_variable: latest_shot
```

Das Ergebnis steht unter `latest_shot.result`. `query` übergibt Query-Parameter
als Mapping; JSON-Nutzdaten stehen unter `body`. Für Text `content_type` und einen
String in `body` verwenden (YAML-Editor). Für Binärdaten `body_base64` und
`content_type` verwenden. Binäre Antworten erscheinen als
`result.base64` und `result.content_type`. Pro Anfrage nur eine Body-Variante verwenden.
Pfade beginnen mit `/api/v1/`; URLs und Query-Strings im Pfad sind nicht erlaubt.
Pfadparameter selbst passend URL-kodieren.

### Zusätzliche Waage oder einen Sensor abonnieren

```yaml
action: decaid.subscribe
data:
  entry_id: DEINE_ENTRY_ID
  channel: /ws/v1/scales/DEINE_WAAGEN_ID/snapshot
```

Eingehende Daten erzeugen `decaid_message` mit `entry_id`, `channel` und `data`.
`decaid.unsubscribe` beendet zusätzliche Abonnements. Die sieben Kernkanäle bleiben
für die Entitäten aktiv. Rohereignisse für Kernkanäle müssen in den Optionen aktiviert
werden; diese Option erzeugt bei Telemetrie viele Ereignisse.

### Gerätesuche über WebSocket

Nach bestehender Verbindung des automatischen Gerätekanals:

```yaml
action: decaid.websocket_send
data:
  entry_id: DEINE_ENTRY_ID
  channel: /ws/v1/devices
  message:
    command: scan
    connect: false
    quick: true
```

### Auf Bezugsentscheidungen reagieren

`decaid_shot` wird für `decision` und `terminal` aus dem Shot-State-Kanal erzeugt.
Das Ereignis enthält die Originalfelder, u.a. `shotId`, `state` und `decision.reason`,
sowie `entry_id`. Nicht jedes Terminal-Ereignis bedeutet einen erfolgreichen Espresso;
für Benachrichtigungen den Entscheidungsgrund prüfen. Unbekannte Gründe bleiben erhalten.

## Verhalten bei Ausfällen

WebSocket-Verbindungen werden mit 1–60 Sekunden Backoff wiederaufgebaut. Werte eines
abgebrochenen Streams werden verworfen, statt dauerhaft einen alten Wert anzuzeigen.
Der Maschinenzustand besitzt einen REST-Fallback. Fehlende Bengle-Funktionen oder
getrennte Waagen verhindern die Einrichtung der App-Integration nicht.
Schreibbefehle werden **nicht automatisch wiederholt**. HTTP-Weiterleitungen werden
nicht verfolgt. TLS-Zertifikate werden geprüft. Diagnosedaten enthalten weder Token
noch Tablet-Adresse oder persönliche Rezeptdaten.

## Entwicklung

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
.venv/bin/pytest -q
.venv/bin/ruff check .
```

GitHub Actions prüft Änderungen mit pytest und Ruff.
Repository: https://github.com/mp0x6/decaid-hass
