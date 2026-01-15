import re
from typing import Any

from playwright.sync_api import Page, Playwright

from .parsing import ISIN_RE, extract_isin_wkn, parse_eur, parse_qty, de_number_to_float

def _accept_cookies(page: Page) -> None:
    try:
        page.get_by_role("button", name="Alle akzeptieren").click(timeout=3000)
    except Exception:
        pass

def _get_login_frame(page: Page):
    iframe_loc = page.locator("#loginModal iframe")
    # Prefer FrameLocator API where available
    if hasattr(page, "frame_locator"):
        try:
            return page.frame_locator("#loginModal iframe")
        except Exception:
            pass
    # Fallback to Frame via content_frame()
    try:
        fr = iframe_loc.content_frame()
        if fr is not None:
            return fr
    except Exception:
        pass
    raise RuntimeError("Could not access login iframe (#loginModal iframe).")


def login_and_open_depot(playwright: Playwright, *, user: str, password: str, depot_label: str | None, headless: bool) -> Page:
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.flatex.de/")
    _accept_cookies(page)
    page.get_by_role("link", name="Login").click()

    frame = _get_login_frame(page)
    frame.get_by_role("textbox", name="Kundennummer / Benutzername").fill(user)
    frame.get_by_role("textbox", name="Passwort").fill(password)

    with page.expect_popup() as popup_info:
        frame.get_by_role("button", name="Anmelden").click()
    page1 = popup_info.value

    page1.goto("https://konto.flatex.de/banking-flatex/accountOverviewFormAction.do")

    if depot_label:
        page1.get_by_text(depot_label, exact=True).click()
    else:
        page1.get_by_text("Depot", exact=False).first.click()

    page1.locator("#depositStatementForm_depositStatementTable").wait_for(state="visible", timeout=20000)
    return page1


def scrape_totals(page: Page) -> dict[str, Any]:
    table = page.locator("#depositStatementForm_depositStatementTable")
    table.wait_for(state="visible", timeout=20000)

    rowgroups = table.get_by_role("rowgroup")
    totals: dict[str, Any] = {}

    for i in range(rowgroups.count()):
        rg = rowgroups.nth(i)
        txt = rg.inner_text()
        if "Aktueller Gesamtwert" in txt or "Gesamteinstandswert" in txt:
            rows = rg.get_by_role("row")
            for r in range(rows.count()):
                row = rows.nth(r)
                cells = row.get_by_role("cell")
                if cells.count() < 3:
                    continue
                label = cells.nth(0).inner_text().strip()
                if "Aktueller Gesamtwert" in label:
                    totals["total_current_value"] = parse_eur(cells.nth(2).inner_text().strip())
                if "Gesamteinstandswert" in label:
                    totals["total_buy_value"] = parse_eur(cells.nth(2).inner_text().strip())
            break

    return totals


def scrape_positions(page: Page, *, debug_dump: bool = False) -> tuple[list[dict[str, Any]], dict | None]:
    table = page.locator("#depositStatementForm_depositStatementTable")
    table.wait_for(state="visible", timeout=20000)

    rowgroups = table.get_by_role("rowgroup")

    data_group = None
    max_rows = -1
    for i in range(rowgroups.count()):
        rg = rowgroups.nth(i)
        rc = rg.get_by_role("row").count()
        if rc > max_rows:
            max_rows = rc
            data_group = rg

    rows = data_group.get_by_role("row")
    n = rows.count()

    def row_cells_text(r):
        cells = r.get_by_role("cell")
        return [cells.nth(i).inner_text().replace("\xa0", " ").strip() for i in range(cells.count())]

    if debug_dump:
        dump = []
        for i in range(n):
            r = rows.nth(i)
            texts = row_cells_text(r)
            dump.append({"i": i, "cells": texts, "row_text": r.inner_text().replace("\xa0"," ").strip()})
        return [], {"debug_rows": dump}

    def is_blank_row(texts: list[str]) -> bool:
        return all((t.strip() == "") for t in texts)

    def is_main_row(texts: list[str]) -> bool:
        return any("Stk." in t for t in texts)

    def is_detail_row(texts: list[str]) -> bool:
        joined = " ".join(texts)
        if not ISIN_RE.search(joined):
            return False
        if not re.search(r"\b\d{2}\.\d{2}\.\d{4}\b", joined):
            return False
        if ":" not in joined:
            return False
        return len(texts) >= 6

    positions: list[dict[str, Any]] = []
    pending_main: list[str] | None = None

    i = 0
    while i < n:
        texts = row_cells_text(rows.nth(i))

        if is_blank_row(texts):
            i += 1
            continue

        joined = " ".join(texts)
        if "Clearstream" in joined or "Kategorie" in joined or "Sperre" in joined:
            i += 1
            continue

        if is_main_row(texts):
            pending_main = texts
            i += 1
            continue

        if is_detail_row(texts):
            detail = texts

            layout_b = (
                len(detail) >= 9
                and ISIN_RE.fullmatch(detail[1] or "") is not None
                and (detail[2] or "").strip() == "|"
            )

            if layout_b:
                isin = detail[1]
                wkn = detail[3] if detail[3] else None
                buy_price_raw = detail[4]
                date_raw = detail[5]
                day_raw = detail[6]
                buy_value_raw = detail[7]
                dev_pct_raw = detail[8]
            else:
                isin_wkn_text = detail[0] if len(detail) > 0 else ""
                isin, wkn = extract_isin_wkn(isin_wkn_text)
                buy_price_raw = detail[1] if len(detail) > 1 else ""
                date_raw = detail[2] if len(detail) > 2 else ""
                day_raw = detail[3] if len(detail) > 3 else ""
                buy_value_raw = detail[4] if len(detail) > 4 else ""
                dev_pct_raw = detail[5] if len(detail) > 5 else ""

            if not isin:
                pending_main = None
                i += 1
                continue

            main = pending_main
            if not main or not is_main_row(main):
                pending_main = None
                i += 1
                continue

            name = main[0] if len(main) > 0 else ""
            qty_raw = main[1] if len(main) > 1 else ""
            exchange = main[2] if len(main) > 2 else ""
            last_price_raw = main[3] if len(main) > 3 else ""
            current_value_raw = main[4] if len(main) > 4 else ""
            dev_abs_raw = main[5] if len(main) > 5 else ""

            positions.append({
                "name": name,
                "isin": isin,
                "wkn": wkn,
                "exchange": exchange,
                "qty": parse_qty(qty_raw),
                "qty_raw": qty_raw,
                "last_price": de_number_to_float(last_price_raw),
                "last_price_raw": last_price_raw,
                "current_value": parse_eur(current_value_raw),
                "current_value_raw": current_value_raw,
                "buy_price": de_number_to_float(buy_price_raw),
                "buy_price_raw": buy_price_raw,
                "buy_value": parse_eur(buy_value_raw),
                "buy_value_raw": buy_value_raw,
                "dev_abs": parse_eur(dev_abs_raw),
                "dev_abs_raw": dev_abs_raw,
                "dev_pct_raw": dev_pct_raw,
                "last_update_raw": date_raw,
                "day_change_raw": day_raw,
            })

            pending_main = None
            i += 1
            continue

        i += 1

    return positions, None
