# --- Flatex credentials ---
$env:FLATEX_USER="DEIN_USER"
$env:FLATEX_PASS="DEIN_PASS"
$env:FLATEX_DEPOT_LABEL="***123 Depot - Meier"

# --- Runtime ---
$env:HEADLESS="true"

# --- MySQL ---
$env:MYSQL_ENABLED="true"
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="flatex"
$env:MYSQL_PASS="secret"
$env:MYSQL_DB="flatex"

# --- InfluxDB ---
$env:INFLUX_ENABLED="true"
$env:INFLUX_URL="http://localhost:8086"
$env:INFLUX_ORG="my-org"
$env:INFLUX_BUCKET="flatex"
$env:INFLUX_TOKEN="my-token"

# --- optional Debug ---
# $env:DEBUG_TABLE="true"

# --- run ---
python -m src.flatex_scraper
