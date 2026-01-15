from __future__ import annotations

from datetime import datetime
from .config import InfluxConfig

def write(cfg: InfluxConfig, ts_utc: datetime, totals: dict, positions: list[dict]) -> None:
    try:
        from influxdb_client import InfluxDBClient, Point
        from influxdb_client.client.write_api import SYNCHRONOUS
    except Exception as e:
        raise RuntimeError(
            "Influx enabled but influxdb-client is not installed. Add it to requirements.txt: influxdb-client==1.41.0"
        ) from e

    client = InfluxDBClient(url=cfg.url, token=cfg.token, org=cfg.org, timeout=cfg.timeout_ms)
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        points = []

        pt = Point("portfolio").time(ts_utc)
        pt = pt.field("total_current_value", float(totals.get("total_current_value") or 0.0))
        pt = pt.field("total_buy_value", float(totals.get("total_buy_value") or 0.0))
        points.append(pt)

        for pos in positions:
            isin = pos.get("isin")
            if not isin:
                continue
            p = Point("position").tag("isin", isin).time(ts_utc)
            if pos.get("wkn"):
                p = p.tag("wkn", str(pos["wkn"]))
            if pos.get("exchange"):
                p = p.tag("exchange", str(pos["exchange"]))

            p = p.field("qty", float(pos.get("qty") or 0.0))
            p = p.field("current_value", float(pos.get("current_value") or 0.0))
            p = p.field("buy_value", float(pos.get("buy_value") or 0.0))
            p = p.field("last_price", float(pos.get("last_price") or 0.0))
            p = p.field("buy_price", float(pos.get("buy_price") or 0.0))
            p = p.field("dev_abs", float(pos.get("dev_abs") or 0.0))

            points.append(p)

        write_api.write(bucket=cfg.bucket, org=cfg.org, record=points)
        write_api.close()
    finally:
        client.close()
