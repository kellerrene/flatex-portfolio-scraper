import os
from dataclasses import dataclass

def env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

def env_str(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    if v is None:
        return default
    v = v.strip()
    return v if v != "" else default

def env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or v.strip() == "":
        return default
    return int(v)

@dataclass(frozen=True)
class FlatexConfig:
    user: str
    password: str
    depot_label: str | None
    headless: bool

@dataclass(frozen=True)
class MysqlConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    connect_timeout: int = 10

@dataclass(frozen=True)
class InfluxConfig:
    url: str
    token: str
    org: str
    bucket: str
    timeout_ms: int = 10_000

@dataclass(frozen=True)
class AppConfig:
    flatex: FlatexConfig
    mysql: MysqlConfig | None
    influx: InfluxConfig | None
    output_json_path: str | None
    debug_table: bool

def load_flatex_config() -> FlatexConfig:
    user = os.environ["FLATEX_USER"]
    pw = os.environ["FLATEX_PASS"]
    depot_label = env_str("FLATEX_DEPOT_LABEL")
    headless = env_bool("HEADLESS", default=True)
    return FlatexConfig(user=user, password=pw, depot_label=depot_label, headless=headless)

def load_mysql_config() -> MysqlConfig | None:
    if not env_bool("MYSQL_ENABLED", default=False):
        return None

    def req(k: str) -> str:
        v = os.environ.get(k)
        if not v:
            raise RuntimeError(f"Missing required env var: {k}")
        return v

    host = req("MYSQL_HOST")
    port = env_int("MYSQL_PORT", 3306)
    user = req("MYSQL_USER")
    password = req("MYSQL_PASS")
    database = req("MYSQL_DB")
    timeout = env_int("MYSQL_CONNECT_TIMEOUT", 10)
    return MysqlConfig(host=host, port=port, user=user, password=password, database=database, connect_timeout=timeout)

def load_influx_config() -> InfluxConfig | None:
    if not env_bool("INFLUX_ENABLED", default=False):
        return None

    def req(k: str) -> str:
        v = os.environ.get(k)
        if not v:
            raise RuntimeError(f"Missing required env var: {k}")
        return v

    url = req("INFLUX_URL")
    token = req("INFLUX_TOKEN")
    org = req("INFLUX_ORG")
    bucket = req("INFLUX_BUCKET")
    timeout_ms = env_int("INFLUX_TIMEOUT_MS", 10_000)
    return InfluxConfig(url=url, token=token, org=org, bucket=bucket, timeout_ms=timeout_ms)

def load_app_config() -> AppConfig:
    flatex = load_flatex_config()
    mysql = load_mysql_config()
    influx = load_influx_config()
    output_json_path = env_str("OUTPUT_JSON_PATH")
    debug_table = env_bool("DEBUG_TABLE", default=False)
    return AppConfig(
        flatex=flatex,
        mysql=mysql,
        influx=influx,
        output_json_path=output_json_path,
        debug_table=debug_table,
    )
