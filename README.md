# Flatex Portfolio Tracker

Dieses Projekt ist ein **Portfolio-Tracker für Flatex (Deutschland)**, der die Entwicklung einzelner Wertpapiere sowie des Gesamtportfolios über die Zeit erfasst und in **MySQL / MariaDB** und/oder **InfluxDB** speichert.

## Motivation

Bei langfristigen Portfoliostrategien reicht ein aktueller Depotstand nicht aus. Entscheidend sind:
- der zeitliche **Wertverlauf einzelner Assets**,
- die Entwicklung von **Assetklassen**,
- sowie die **Gewichtung im Gesamtportfolio**.

Grundlage dafür sind **historische Bewegungsdaten** des Portfolios in einer weiterverarbeitbaren Form. Genau hier setzt dieses Projekt an.

## Funktionsumfang

- Automatisches Auslesen des Flatex-Depots (Web-Scraping mit Playwright)
- Speicherung von:
  - Portfolio-Snapshots (Gesamtwert, Einstandswert)
  - Einzelpositionen (ISIN, Stückzahl, Preise, Werte)
- Persistenz wahlweise in:
  - MySQL / MariaDB
  - InfluxDB (Zeitreihen)
- Ausgabe der Rohdaten als JSON
- Headless-Betrieb unter Linux
- Lauffähig unter Windows
- Docker-Setup inkl. Beispiel-Cronjob

> **Hinweis:** Entwickelt und getestet für die **deutsche Flatex-Weboberfläche**.  
> Ob die österreichische Variante kompatibel ist, muss geprüft werden.

## Projektstruktur

```
.
├─ src/                # Python-Quellcode
├─ docker/             # Dockerfile & Compose
├─ docs/               # Doku zu Docker, MySQL, InfluxDB
├─ scripts/            # Startskripte (Windows / Linux)
├─ .env.example        # Beispiel-Konfiguration
├─ requirements.txt
└─ README.md
```

Im Verzeichnis `docs/` befindet sich zusätzliche Dokumentation zu:
- Docker-Betrieb
- MySQL / MariaDB Schema
- InfluxDB Messkonzept und Beispiel-Queries

## Schnellstart

### Windows
1. `scripts/run.ps1` öffnen
2. ENV-Variablen (Flatex, MySQL, Influx) anpassen
3. Skript ausführen

### Linux / Docker
1. `.env.example` nach `.env` kopieren und anpassen
2. `docker compose build`
3. `docker compose run --rm flatex-scraper`

Ein Beispiel für einen stündlichen Cronjob (werktags) ist enthalten.

## Hinweis zur Entstehung

⚠️ **Wichtiger Transparenzhinweis**

- Quellcode **und** Dokumentation sind zu **100 % KI-generiert**
- Es wurden KI-Engineering-Prozesse und -Tools von **Explicatis** angewendet
- Der Autor besitzt **keine Entwicklungskompetenz in Python**
- Umsetzung inkl. Qualitätssicherung, Tests und Dokumentation:
  **ca. 3 Stunden von Idee bis GitHub-Release**

Das Projekt dient als **praxisnahes Beispiel**, wie KI-gestützte Softwareentwicklung auch für Nicht-Python-Entwickler funktionieren kann.

## Lizenz

MIT License – Nutzung, Anpassung und Weiterverwendung ausdrücklich erlaubt.
