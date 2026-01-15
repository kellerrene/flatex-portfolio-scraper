import json
import sys

from playwright.sync_api import sync_playwright

from .config import load_app_config
from .scraping import login_and_open_depot, scrape_positions, scrape_totals
from .util import utc_now, write_json_file

def main() -> int:
    cfg = load_app_config()

    with sync_playwright() as playwright:
        page = login_and_open_depot(
            playwright,
            user=cfg.flatex.user,
            password=cfg.flatex.password,
            depot_label=cfg.flatex.depot_label,
            headless=cfg.flatex.headless,
        )

        if cfg.debug_table:
            _, debug_payload = scrape_positions(page, debug_dump=True)
            if debug_payload:
                print(json.dumps(debug_payload, ensure_ascii=False))
            return 0

        positions, _ = scrape_positions(page, debug_dump=False)
        totals = scrape_totals(page)

        ts_utc = utc_now()
        result = {"ts": ts_utc.isoformat(), "positions": positions, **totals}

        if cfg.output_json_path:
            try:
                write_json_file(cfg.output_json_path, result)
            except Exception as e:
                print(f"WARN: Could not write OUTPUT_JSON_PATH={cfg.output_json_path}: {e}", file=sys.stderr)

    totals_out = {k: result.get(k) for k in ("total_current_value", "total_buy_value") if k in result}
    positions_out = result.get("positions", [])

    if cfg.mysql:
        try:
            from .persistence_mysql import write_snapshot_and_positions
            write_snapshot_and_positions(cfg.mysql, ts_utc, totals_out, positions_out)
            print("MySQL: write OK", file=sys.stderr)
        except Exception as e:
            print(f"MySQL: write FAILED: {e}", file=sys.stderr)

    if cfg.influx:
        try:
            from .persistence_influx import write as influx_write
            influx_write(cfg.influx, ts_utc, totals_out, positions_out)
            print("InfluxDB: write OK", file=sys.stderr)
        except Exception as e:
            print(f"InfluxDB: write FAILED: {e}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
