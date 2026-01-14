<!-- docs/mysql.md -->
# MySQL / MariaDB

## Überblick

Optional kann der Scraper jeden Abruf in **MySQL/MariaDB** persistieren.

Es werden zwei Tabellen genutzt:

- `portfolio_snapshot` (Gesamtwerte pro Abruf)
- `portfolio_position` (Positionen pro Abruf und ISIN)

Wichtiges Design:
- **ein einheitlicher Zeitstempel pro Abruf**
- künstlicher Primärschlüssel (`BIGINT AUTO_INCREMENT`)
- `UNIQUE(ts, isin)` bei Positionen
- Index auf `isin`

## Aktivieren (Environment)

```env
MYSQL_ENABLED=true
MYSQL_HOST=...
MYSQL_PORT=3306
MYSQL_USER=...
MYSQL_PASS=...
MYSQL_DB=...
MYSQL_CONNECT_TIMEOUT=10