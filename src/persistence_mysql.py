from __future__ import annotations

from datetime import datetime
from .config import MysqlConfig

MYSQL_CREATE_SNAPSHOT = """
CREATE TABLE IF NOT EXISTS portfolio_snapshot (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ts DATETIME(6) NOT NULL,

    total_current_value DECIMAL(18,2) NOT NULL,
    total_buy_value DECIMAL(18,2) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_portfolio_snapshot_ts (ts)
) ENGINE=InnoDB;
"""

MYSQL_CREATE_POSITION = """
CREATE TABLE IF NOT EXISTS portfolio_position (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ts DATETIME(6) NOT NULL,

    isin CHAR(12) NOT NULL,
    wkn  CHAR(6) NULL,
    name VARCHAR(255) NULL,
    exchange VARCHAR(64) NULL,

    qty DECIMAL(18,6) NOT NULL,
    last_price DECIMAL(18,6) NULL,
    current_value DECIMAL(18,2) NULL,
    buy_price DECIMAL(18,6) NULL,
    buy_value DECIMAL(18,2) NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_portfolio_position_ts_isin (ts, isin),
    KEY idx_portfolio_position_isin (isin)
) ENGINE=InnoDB;
"""

def ensure_schema(cursor) -> None:
    cursor.execute(MYSQL_CREATE_SNAPSHOT)
    cursor.execute(MYSQL_CREATE_POSITION)

def write_snapshot_and_positions(cfg: MysqlConfig, ts_utc: datetime, totals: dict, positions: list[dict]) -> None:
    try:
        import mysql.connector
    except Exception as e:
        raise RuntimeError(
            "MySQL enabled but mysql-connector-python is not installed. Add it to requirements.txt: mysql-connector-python==8.3.0"
        ) from e

    conn = mysql.connector.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database,
        connection_timeout=cfg.connect_timeout,
        autocommit=False,
    )
    try:
        cur = conn.cursor()
        ensure_schema(cur)
        conn.commit()

        ts_naive = ts_utc.replace(tzinfo=None)

        total_current_value = float(totals.get("total_current_value", 0.0) or 0.0)
        total_buy_value = float(totals.get("total_buy_value", 0.0) or 0.0)

        cur.execute(
            """
            INSERT INTO portfolio_snapshot (ts, total_current_value, total_buy_value)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
              total_current_value = VALUES(total_current_value),
              total_buy_value = VALUES(total_buy_value)
            """,
            (ts_naive, total_current_value, total_buy_value),
        )

        rows = []
        for p in positions:
            isin = p.get("isin")
            if not isin:
                continue
            rows.append(
                (
                    ts_naive,
                    isin,
                    p.get("wkn"),
                    p.get("name"),
                    p.get("exchange"),
                    float(p.get("qty") or 0.0),
                    float(p.get("last_price") or 0.0),
                    float(p.get("current_value") or 0.0),
                    float(p.get("buy_price") or 0.0),
                    float(p.get("buy_value") or 0.0),
                )
            )

        if rows:
            cur.executemany(
                """
                INSERT INTO portfolio_position
                  (ts, isin, wkn, name, exchange, qty, last_price, current_value, buy_price, buy_value)
                VALUES
                  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  wkn = VALUES(wkn),
                  name = VALUES(name),
                  exchange = VALUES(exchange),
                  qty = VALUES(qty),
                  last_price = VALUES(last_price),
                  current_value = VALUES(current_value),
                  buy_price = VALUES(buy_price),
                  buy_value = VALUES(buy_value)
                """,
                rows,
            )

        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass
