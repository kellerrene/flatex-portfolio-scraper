# flatex-portfolio-tracker

Dieses Projekt ist ein **Portfolio-Scraper für Flatex (Deutschland)**, der die Depotübersicht automatisiert ausliest und die Daten strukturiert für eine langfristige Weiterverarbeitung speichert.

## Motivation

Bei langfristigen Portfoliostrategien reicht eine Momentaufnahme nicht aus. Entscheidend sind:

- der **Wertverlauf einzelner Assets**
- die **Entwicklung von Assetklassen**
- die **Gewichtung im Gesamtportfolio über die Zeit**

Grundlage dafür sind **historische Bewegungsdaten** des Portfolios in einer maschinenlesbaren, weiterverarbeitbaren Form.  
Genau hier setzt dieses Projekt an.

## Ziel des Projekts

Dieses Tool ermöglicht es privaten Anlegern und technisch interessierten Nutzern,

- Portfoliodaten regelmäßig automatisiert abzurufen
- diese **zeitgestempelt** zu speichern
- und für eigene Auswertungen, Visualisierungen oder Rebalancing-Analysen zu nutzen

Die Daten können wahlweise oder parallel abgelegt werden in:

- **MySQL / MariaDB** (relationale Historisierung)
- **InfluxDB 2.x** (Zeitreihenanalyse, ideal für Charts & Dashboards)

## Funktionsumfang

- automatischer Login bei Flatex (DE)
- Auslesen aller Depotpositionen inkl.:
  - ISIN, WKN
  - Stückzahl
  - aktueller Wert
  - Einstandswerte
- Speicherung mit **einem konsistenten Zeitstempel pro Abruf**
- optionaler JSON-Export
- lauffähig:
  - unter **Windows**
  - **headless unter Linux**
  - vollständig **dockerisiert**
- Beispiel für **Cron-Ausführung** enthalten (z. B. stündlich an Werktagen)

## Technik

- Python
- Playwright (Browser-Automation)
- MySQL / MariaDB (optional)
- InfluxDB 2.x (optional)
- Docker & Docker Compose

## Einsatzszenarien

- Langfristiges Performance-Tracking
- Visualisierung des Portfolios (z. B. Grafana)
- Analyse von Assetklassen-Gewichtungen
- Basis für eigene Finanz- und Rebalancing-Tools
- Home-Assistant- oder BI-Integration

## Einschränkungen

- Entwickelt und getestet **für die deutsche Flatex-Webseite**
- Ob die österreichische Flatex-Seite kompatibel ist, muss geprüft werden
- Änderungen an der Flatex-Oberfläche können Anpassungen erfordern

## Zielgruppe

Dieses Projekt richtet sich an:

- technisch affine Privatanleger
- Entwickler mit Interesse an Finanzdaten
- Nutzer, die ihr Portfolio **nicht nur beobachten, sondern verstehen** wollen

## Lizenz

MIT License – freie Nutzung, Anpassung und Weiterverwendung.
