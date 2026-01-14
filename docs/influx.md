# InfluxDB 2.x

## Überblick

Optional schreibt das Tool Zeitreihen nach **InfluxDB 2.x**.  
Ideal für schnelle Charts (z. B. Influx Data Explorer / Grafana).

Es werden zwei Measurements geschrieben:

- `portfolio` (Gesamtwerte)
- `position` (je ISIN)

## Aktivieren (Environment)

```env
INFLUX_ENABLED=true
INFLUX_URL=http://influxdb:8086
INFLUX_TOKEN=...
INFLUX_ORG=...
INFLUX_BUCKET=...
INFLUX_TIMEOUT_MS=10000
```

Hinweis:
- In Docker-Netzwerken ist `INFLUX_URL=http://influxdb:8086` korrekt, wenn der Service `influxdb` heißt.
- Außerhalb Docker meist `http://<host-ip>:8086` oder `http://localhost:8086`.

## Datenmodell

### Measurement: portfolio

Fields:
- `total_current_value` (float)
- `total_buy_value` (float)

Tags:
- keine (optional erweiterbar)

Time:
- Abrufzeitpunkt (UTC)

### Measurement: position

Tags:
- `isin` (immer)
- optional: `wkn`, `exchange`

Fields:
- `qty`
- `current_value`
- `buy_value`
- `last_price`
- `buy_price`
- `dev_abs`

Time:
- **Abrufzeitpunkt (UTC)** – für alle Positionen eines Abrufs identisch

## Flux Beispiele

### Portfolio-Gesamtwert als Linie

```flux
from(bucket: v.bucket)
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "portfolio" and r._field == "total_current_value")
  |> aggregateWindow(every: 1h, fn: last, createEmpty: false)
  |> yield(name: "total_current_value")
```

### Wertentwicklung pro ISIN (jede ISIN eine Linie)

```flux
from(bucket: v.bucket)
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "position" and r._field == "current_value")
  |> group(columns: ["isin"])
  |> aggregateWindow(every: 1h, fn: last, createEmpty: false)
  |> yield(name: "current_value_by_isin")
```

### Gewichtung (current_value / Portfolio total)

Hinweis: Das ist in Flux etwas aufwändiger, da zwei Measurements kombiniert werden.

```flux
positions =
  from(bucket: v.bucket)
    |> range(start: -30d)
    |> filter(fn: (r) => r._measurement == "position" and r._field == "current_value")
    |> aggregateWindow(every: 1h, fn: last, createEmpty: false)
    |> keep(columns: ["_time","_value","isin"])

totals =
  from(bucket: v.bucket)
    |> range(start: -30d)
    |> filter(fn: (r) => r._measurement == "portfolio" and r._field == "total_current_value")
    |> aggregateWindow(every: 1h, fn: last, createEmpty: false)
    |> keep(columns: ["_time","_value"])
    |> rename(columns: {_value: "total"})

join(tables: {p: positions, t: totals}, on: ["_time"])
  |> map(fn: (r) => ({ r with weight: float(v: r._value) / float(v: r.total) }))
  |> keep(columns: ["_time","isin","weight"])
  |> group(columns: ["isin"])
  |> yield(name: "weight_by_isin")
```

## Troubleshooting

### `Failed to resolve 'influxdb'`
- Du nutzt vermutlich Docker-Hostname außerhalb von Docker.
- Lösung: `INFLUX_URL` auf Host-IP/Hostname setzen, z. B. `http://192.168.x.x:8086`.

### „write OK, aber keine Daten sichtbar“
- Bucket/Org prüfen
- Token-Rechte prüfen (write access)
- im Data Explorer `range()` ausreichend groß wählen (z. B. `-24h`, `-30d`)
