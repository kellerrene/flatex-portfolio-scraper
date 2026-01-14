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
```

## Schema

Das Tool legt die Tabellen bei Bedarf selbst an (`CREATE TABLE IF NOT EXISTS ...`).

### portfolio_snapshot (Beispiel)

- `ts` (UTC, DATETIME(6))
- `total_current_value`
- `total_buy_value`

### portfolio_position (Beispiel)

- `ts` (UTC, DATETIME(6))
- `isin`, `wkn`, `name`, `exchange`
- `qty`, `last_price`, `current_value`, `buy_price`, `buy_value`

## Hinweise

- `ts` wird in MySQL als timezone-naive `DATETIME(6)` gespeichert, **immer als UTC**.
- Re-Run mit identischem Timestamp (selten) wird über Upsert (`ON DUPLICATE KEY UPDATE`) sauber behandelt.

## Typische Abfragen

### Letzter Snapshot

```sql
SELECT *
FROM portfolio_snapshot
ORDER BY ts DESC
LIMIT 1;
```

### Verlauf eines Assets (ISIN)

```sql
SELECT ts, current_value, qty, last_price, buy_value
FROM portfolio_position
WHERE isin = 'IE00B5BMR087'
ORDER BY ts;
```

### Portfolio-Gewichtung pro Zeitpunkt (aus current_value)

```sql
SELECT
  p.ts,
  p.isin,
  p.current_value,
  s.total_current_value,
  (p.current_value / s.total_current_value) AS weight
FROM portfolio_position p
JOIN portfolio_snapshot s ON s.ts = p.ts
WHERE p.ts >= NOW() - INTERVAL 30 DAY
ORDER BY p.ts, p.isin;
```
