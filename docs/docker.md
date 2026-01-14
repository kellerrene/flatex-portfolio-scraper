# Docker

## Überblick

Das Projekt kann vollständig in Docker laufen – inkl. Playwright im **Headless-Modus**.  
Empfohlen für den produktiven Betrieb (z. B. mit Cron auf dem Host).

## Voraussetzungen

- Docker Engine
- Docker Compose (Plugin)

## Dateien

- `Dockerfile` – baut das Runtime-Image inkl. Abhängigkeiten
- `docker-compose.yml` – Service-Definition (Scraper)
- `.env` – lokale Secrets/Settings (nicht committen)
- `.env.example` – Vorlage ohne Secrets

## .env anlegen

```bash
cp .env.example .env
```

Dann Werte eintragen (Flatex, MySQL/Influx optional).

## Build & Run

Im Projekt-Root:

```bash
docker compose build
docker compose run --rm flatex-scraper
```

Logs erscheinen direkt in der Konsole.

## Headless vs. UI

Standard ist typischerweise headless. Gesteuert über:

- `HEADLESS=true|false`

Hinweis: UI-Betrieb in Docker erfordert zusätzliche X11/VNC-Konfiguration und ist hier nicht Fokus.

## JSON-Output / Datei

Das Skript schreibt JSON immer nach stdout. Optional zusätzlich als Datei:

- `OUTPUT_JSON_PATH=/out/latest.json`

Wenn du im Compose ein Volume nach `/out` bindest, kannst du den letzten Stand einfach abholen.

## Debug: Tabellenstruktur ausgeben

Falls sich die Flatex-Oberfläche ändert, hilft ein Debug-Dump der Table-Rows:

- `DEBUG_TABLE=true`

Dann schreibt das Skript eine strukturierte `debug_rows`-Ausgabe nach stderr.

## Beispiel-Cron (Host)

Siehe `cron/crontab.example`.

Empfehlung: Cron läuft auf dem Host und ruft `docker compose run --rm ...` auf.
