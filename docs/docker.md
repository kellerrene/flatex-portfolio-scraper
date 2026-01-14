<!-- docs/docker.md -->
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
