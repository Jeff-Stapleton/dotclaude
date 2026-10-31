#!/usr/bin/env python3
"""Grocery Tracker workbook helper.

Commands:
  init PATH               Create a blank tracker workbook (refuses to overwrite).
  upsert PATH DATA.json   Add or update purchases, price checks, orders and catalog items.
  catalog PATH            Print the item catalog with purchase history and best prices as JSON.
  summary PATH DATE       Print per-store totals for one trip date (YYYY-MM-DD).

DATA.json shape (every list is optional):
{
  "catalog":      [{"item", "category", "unit", "usual_amount", "preferred_store", "on_hand", "reorder_at", "notes"}],
  "purchases":    [{"date", "store", "fulfillment", "item", "product", "brand", "sku", "pack_size",
                    "pack_unit", "qty", "price", "regular_price", "by_weight", "notes", "category"?}],
  "price_checks": [{"date", "store", "item", "product", "sku", "pack_size", "pack_unit", "price", "notes"}],
  "orders":       [{"date", "store", "order_number", "fulfillment", "fees", "tip", "tax", "status", "notes"}]
}

Rows are matched before writing, so re-running with corrected data updates rows instead of
duplicating them: purchases and price checks on (date, store, sku or product); orders on
(date, store, order number); catalog on item name. Only fields present in DATA.json are written.

The workbook keeps formulas (line totals, price per unit, catalog stats, summary), so this
script never writes computed values; `catalog` and `summary` compute their numbers in Python.
"""
import datetime as dt
import json
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.datavalidation import DataValidation

LOG, CHECKS, CAT, ORDERS, SUMMARY, README = (
    "Purchase Log", "Price Checks", "Item Catalog", "Orders", "Summary", "Read Me")
END = 5000  # last row covered by cross-sheet formula ranges
PREFILL = {LOG: 500, CHECKS: 300, CAT: 150, ORDERS: 200}
DEFAULT_STORES = ["Walmart", "Sam's Club"]
DEFAULT_CATEGORIES = ["Meat", "Dairy & Protein", "Fresh Produce", "Frozen",
                      "Bread, Pasta & Breakfast", "Canned & Jarred", "Drinks & Lunch Snacks"]

FONT = "Arial"
f_base = Font(name=FONT, size=10)
f_input = Font(name=FONT, size=10, color="0000FF")
f_header = Font(name=FONT, size=10, bold=True, color="FFFFFF")
f_title = Font(name=FONT, size=14, bold=True)
f_bold = Font(name=FONT, size=10, bold=True)
HEADER_FILL = PatternFill("solid", fgColor="1F4E3D")
INPUT_FILL = PatternFill("solid", fgColor="FFFF00")
_side = Side(style="thin", color="BFBFBF")
BORDER = Border(top=_side, bottom=_side, left=_side, right=_side)
USD = '$#,##0.00;($#,##0.00);"-"'
USD_UNIT = "$#,##0.000"
DATE_FMT = "yyyy-mm-dd"

PL, PC, IC, OR = (f"'{LOG}'!", f"'{CHECKS}'!", f"'{CAT}'!", f"{ORDERS}!")

# Per-sheet layout: headers, input field -> column, formula column -> template, number formats, widths.
SHEETS = {
    LOG: {
        "headers": ["Purchase Date", "Store", "Fulfillment", "Category", "Item", "Product", "Brand",
                    "Store Item #", "Pack Size", "Pack Unit", "Qty", "Price per Pack", "Line Total",
                    "Price per Unit", "Per", "Regular Price per Pack", "Savings", "Priced by Weight", "Notes"],
        "inputs": {"date": "A", "store": "B", "fulfillment": "C", "item": "E", "product": "F", "brand": "G",
                   "sku": "H", "pack_size": "I", "pack_unit": "J", "qty": "K", "price": "L",
                   "regular_price": "P", "by_weight": "R", "notes": "S"},
        "formulas": {
            "D": f'=IF(E{{r}}="","",IFERROR(INDEX({IC}$B$2:$B${END},MATCH(E{{r}},{IC}$A$2:$A${END},0)),""))',
            "M": '=IF(OR(K{r}="",L{r}=""),"",K{r}*L{r})',
            "N": '=IF(OR(I{r}="",L{r}="",I{r}=0),"",L{r}/I{r})',
            "O": '=IF(J{r}="","","per "&J{r})',
            "Q": '=IF(OR(P{r}="",L{r}="",K{r}=""),"",(P{r}-L{r})*K{r})',
        },
        "formats": {"A": DATE_FMT, "H": "@", "L": USD, "M": USD, "N": USD_UNIT, "P": USD, "Q": USD},
        "widths": [12, 12, 11, 22, 22, 58, 18, 13, 9, 8, 6, 11, 11, 11, 9, 12, 10, 10, 52],
        "key": "E", "freeze": "F2",
    },
    CHECKS: {
        "headers": ["Date", "Store", "Item", "Product", "Store Item #", "Pack Size", "Pack Unit",
                    "Price per Pack", "Price per Unit", "Per", "Notes"],
        "inputs": {"date": "A", "store": "B", "item": "C", "product": "D", "sku": "E", "pack_size": "F",
                   "pack_unit": "G", "price": "H", "notes": "K"},
        "formulas": {
            "I": '=IF(OR(F{r}="",H{r}="",F{r}=0),"",H{r}/F{r})',
            "J": '=IF(G{r}="","","per "&G{r})',
        },
        "formats": {"A": DATE_FMT, "E": "@", "H": USD, "I": USD_UNIT},
        "widths": [12, 12, 22, 62, 13, 9, 8, 11, 11, 9, 34],
        "key": "C", "freeze": "D2",
    },
    CAT: {
        "headers": ["Item", "Category", "Unit Basis", "Usual Amount", "Preferred Store", "Times Bought",
                    "Last Purchased", "Total Spent", "Lowest Price per Unit Paid",
                    "Lowest Price per Unit in Price Checks", "On Hand", "Reorder At", "Status", "Notes"],
        "inputs": {"item": "A", "category": "B", "unit": "C", "usual_amount": "D", "preferred_store": "E",
                   "on_hand": "K", "reorder_at": "L", "notes": "N"},
        "formulas": {
            "F": f'=IF($A{{r}}="","",COUNTIFS({PL}$E$2:$E${END},$A{{r}}))',
            "G": f'=IF($A{{r}}="","",IF(COUNTIFS({PL}$E$2:$E${END},$A{{r}})=0,"",'
                 f'_xlfn.MAXIFS({PL}$A$2:$A${END},{PL}$E$2:$E${END},$A{{r}})))',
            "H": f'=IF($A{{r}}="","",SUMIFS({PL}$M$2:$M${END},{PL}$E$2:$E${END},$A{{r}}))',
            "I": f'=IF($A{{r}}="","",IF(COUNTIFS({PL}$E$2:$E${END},$A{{r}})=0,"",'
                 f'_xlfn.MINIFS({PL}$N$2:$N${END},{PL}$E$2:$E${END},$A{{r}})))',
            "J": f'=IF($A{{r}}="","",IF(COUNTIFS({PC}$C$2:$C${END},$A{{r}})=0,"",'
                 f'_xlfn.MINIFS({PC}$I$2:$I${END},{PC}$C$2:$C${END},$A{{r}})))',
            "M": '=IF(OR(K{r}="",L{r}=""),"",IF(K{r}<=L{r},"Reorder","OK"))',
        },
        "formats": {"G": DATE_FMT, "H": USD, "I": USD_UNIT, "J": USD_UNIT},
        "widths": [24, 24, 9, 18, 14, 9, 13, 11, 13, 15, 9, 9, 9, 52],
        "key": "A", "freeze": "B2",
    },
    ORDERS: {
        "headers": ["Order Date", "Store", "Order #", "Fulfillment", "Items Subtotal", "Fees", "Tip", "Tax",
                    "Order Total", "Status", "Notes"],
        "inputs": {"date": "A", "store": "B", "order_number": "C", "fulfillment": "D", "fees": "F",
                   "tip": "G", "tax": "H", "status": "J", "notes": "K"},
        "formulas": {
            "E": f'=IF(B{{r}}="","",SUMIFS({PL}$M$2:$M${END},{PL}$B$2:$B${END},B{{r}},{PL}$A$2:$A${END},A{{r}}))',
            "I": '=IF(B{r}="","",E{r}+F{r}+G{r}+H{r})',
        },
        "formats": {"A": DATE_FMT, "C": "@", "E": USD, "F": USD, "G": USD, "H": USD, "I": USD},
        "widths": [12, 12, 18, 11, 13, 10, 10, 10, 12, 12, 70],
        "key": "B", "freeze": "C2",
        "fill_inputs": ["C", "F", "G", "H"],
    },
}


# ---------------------------------------------------------------- helpers
def to_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return dt.date.fromisoformat(str(v)[:10])


def norm(v):
    return str(v).strip().lower() if v not in (None, "") else ""


def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font, cell.fill, cell.border = f_header, HEADER_FILL, BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30


def prep_row(ws, spec, r):
    """Make sure row r has its formulas, fonts, formats and borders."""
    for col, tmpl in spec["formulas"].items():
        cell = ws[f"{col}{r}"]
        if cell.value is None:
            cell.value = tmpl.format(r=r)
        cell.font = f_base
    for col in spec["inputs"].values():
        ws[f"{col}{r}"].font = f_input
    for col in spec.get("fill_inputs", []):
        ws[f"{col}{r}"].fill = INPUT_FILL
    for col, fmt in spec["formats"].items():
        ws[f"{col}{r}"].number_format = fmt
    for c in range(1, len(spec["headers"]) + 1):
        ws.cell(row=r, column=c).border = BORDER


def next_empty_row(ws, spec):
    r = 2
    while ws[f"{spec['key']}{r}"].value not in (None, ""):
        r += 1
    return r


def write_fields(ws, spec, r, record):
    prep_row(ws, spec, r)
    for field, col in spec["inputs"].items():
        if field not in record or record[field] is None:
            continue
        v = record[field]
        if field == "date":
            v = to_date(v)
        elif field in ("sku", "order_number"):
            v = str(v)
        ws[f"{col}{r}"].value = v


def rows_by_key(ws, spec, keyfn):
    out = {}
    r = 2
    while ws[f"{spec['key']}{r}"].value not in (None, ""):
        out.setdefault(keyfn(ws, r), []).append(r)
        r += 1
    return out


def line_key(date, store, sku, product):
    return (str(to_date(date)), norm(store), norm(sku) or norm(product))


def dv_list(formula, title):
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    dv.errorStyle = "warning"  # a warning, so new stores and items can still be typed
    dv.errorTitle = title
    dv.error = "This value isn't in the list. Keep it anyway?"
    return dv


# ---------------------------------------------------------------- init
def init(path):
    if os.path.exists(path):
        sys.exit(f"{path} already exists; refusing to overwrite.")
    wb = Workbook()
    wb.remove(wb.active)
    for name in (LOG, ORDERS, SUMMARY, CAT, CHECKS):
        if name == SUMMARY:
            wb.create_sheet(SUMMARY)
            continue
        spec = SHEETS[name]
        ws = wb.create_sheet(name)
        for i, h in enumerate(spec["headers"], start=1):
            ws.cell(row=1, column=i, value=h)
        style_header(ws, len(spec["headers"]))
        for r in range(2, PREFILL[name] + 2):
            prep_row(ws, spec, r)
        for i, w in enumerate(spec["widths"], start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = spec["freeze"]
        ws.auto_filter.ref = f"A1:{get_column_letter(len(spec['headers']))}{PREFILL[name] + 1}"

    log, chk, cat, orders = wb[LOG], wb[CHECKS], wb[CAT], wb[ORDERS]
    log["I1"].comment = Comment("Amount in one pack, in the Pack Unit. For by-weight items this is an "
                                "estimate until you have the receipt.", "Claude")
    log["N1"].comment = Comment("Price per Pack / Pack Size. Compare this across stores and pack sizes.", "Claude")
    cat["K1"].comment = Comment("How many you have at home, in any count you like. Use the same count in "
                                "Reorder At.", "Claude")
    orders["E1"].comment = Comment("Sum of Purchase Log line totals for this store and date.", "Claude")
    cat.conditional_formatting.add(
        f"M2:M{END}", FormulaRule(formula=['$M2="Reorder"'], fill=PatternFill("solid", fgColor="F4CCCC"),
                                  font=Font(name=FONT, size=10, bold=True, color="9C0006")))

    stores = '"' + ",".join(DEFAULT_STORES) + '"'
    items = f"={IC}$A$2:$A$500"
    for ws, cols in ((log, {"B": stores, "E": items, "C": '"Delivery,Pickup,Shipping,In store"', "R": '"Y,N"'}),
                     (chk, {"B": stores, "C": items}),
                     (orders, {"B": stores, "D": '"Delivery,Pickup,Shipping,In store"',
                               "J": '"In cart,Ordered,Delivered,Cancelled"'})):
        for col, formula in cols.items():
            dv = dv_list(formula, ws[f"{col}1"].value)
            dv.add(f"{col}2:{col}{END}")
            ws.add_data_validation(dv)

    build_summary(wb[SUMMARY])
    build_readme(wb.create_sheet(README))
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    wb.save(path)
    print(f"created {path}")


def build_summary(sm):
    def put(ref, value, font=f_base, fmt=None):
        sm[ref].value, sm[ref].font = value, font
        if fmt:
            sm[ref].number_format = fmt

    put("A1", "Grocery Trip Summary", f_title)
    put("A3", "Trip date", f_bold)
    put("B3", dt.date.today(), f_input, DATE_FMT)
    put("C3", "Change this to summarize a different trip.")
    put("A4", "Budget", f_bold)
    put("B4", None, f_input, USD)
    put("C4", "Budget for this trip.")
    heads = ["Store", "Line Items", "Packs", "Subtotal", "Savings vs Regular", "Fees & Tip", "Tax", "Order Total"]
    for i, h in enumerate(heads, start=1):
        sm.cell(row=6, column=i, value=h)
    style_header(sm, len(heads), row=6)
    for r, store in ((7, DEFAULT_STORES[0]), (8, DEFAULT_STORES[1])):
        c = f"{PL}$B$2:$B${END},$A{r},{PL}$A$2:$A${END},$B$3"
        o = f"{OR}$B$2:$B${END},$A{r},{OR}$A$2:$A${END},$B$3"
        put(f"A{r}", store, Font(name=FONT, size=10, bold=True, color="0000FF"))
        put(f"B{r}", f"=COUNTIFS({c})")
        put(f"C{r}", f"=SUMIFS({PL}$K$2:$K${END},{c})")
        put(f"D{r}", f"=SUMIFS({PL}$M$2:$M${END},{c})", fmt=USD)
        put(f"E{r}", f"=SUMIFS({PL}$Q$2:$Q${END},{c})", fmt=USD)
        put(f"F{r}", f"=SUMIFS({OR}$F$2:$F${END},{o})+SUMIFS({OR}$G$2:$G${END},{o})", fmt=USD)
        put(f"G{r}", f"=SUMIFS({OR}$H$2:$H${END},{o})", fmt=USD)
        put(f"H{r}", f"=D{r}+F{r}+G{r}", fmt=USD)
    put("A9", "Total", f_bold)
    for col in "BCDEFGH":
        put(f"{col}9", f"=SUM({col}7:{col}8)", f_bold, USD if col in "DEFGH" else None)
    put("A10", "Budget remaining", f_bold)
    put("H10", '=IF(B4="","",B4-H9)', f_bold, USD)
    for r in range(7, 10):
        for c in range(1, 9):
            sm.cell(row=r, column=c).border = BORDER
    put("A11", "Fees, tip and tax come from the Orders sheet. Store names in A7:A8 can be changed.")

    for i, h in enumerate(["Category", "=A7", "=A8", "Total"], start=1):
        sm.cell(row=13, column=i, value=h)
    style_header(sm, 4, row=13)
    for i, category in enumerate(DEFAULT_CATEGORIES):
        r = 14 + i
        put(f"A{r}", category, f_input)
        for col, store_ref in (("B", "$B$13"), ("C", "$C$13")):
            put(f"{col}{r}", f"=SUMIFS({PL}$M$2:$M${END},{PL}$D$2:$D${END},$A{r},"
                             f"{PL}$B$2:$B${END},{store_ref},{PL}$A$2:$A${END},$B$3)", fmt=USD)
        put(f"D{r}", f"=B{r}+C{r}", fmt=USD)
    tot = 14 + len(DEFAULT_CATEGORIES)
    put(f"A{tot}", "Total", f_bold)
    for col in "BCD":
        put(f"{col}{tot}", f"=SUM({col}14:{col}{tot - 1})", f_bold, USD)
    for r in range(14, tot + 1):
        for c in range(1, 5):
            sm.cell(row=r, column=c).border = BORDER
    for i, w in enumerate([24, 12, 12, 12, 16, 11, 10, 13], start=1):
        sm.column_dimensions[get_column_letter(i)].width = w


def build_readme(rm):
    rm["A1"].value, rm["A1"].font = "How this workbook works", f_title
    lines = [
        ("Sheets", None),
        ("Purchase Log", "One row per product bought: the price history. Filter by Item to see a price over time."),
        ("Orders", "One row per order: order number, fees, tip, tax and status. Fill the yellow cells from the receipt."),
        ("Summary", "Totals by store and category for one trip date, compared with the budget."),
        ("Item Catalog", "One row per thing you buy regularly. Fill On Hand and Reorder At to use it as a pantry inventory."),
        ("Price Checks", "Prices seen but not bought (usually the other store), for comparing next time."),
        (None, None),
        ("Colors", None),
        ("Blue text", "Values you type. Edit these freely."),
        ("Black text", "Formulas. Don't type over them; they fill in when a row has data."),
        ("Yellow fill", "Fill in from the receipt (Orders sheet)."),
        (None, None),
        ("Adding a trip", None),
        ("1", "Ask Claude to do the grocery shopping; it fills the carts, then logs the order here once you've checked out."),
        ("2", "By hand: add rows on Purchase Log and one row per order on Orders. Formulas extend down hundreds of rows."),
        ("3", "Pick the Item from the dropdown so it matches Item Catalog exactly. Add new items to Item Catalog first."),
        ("4", "Price per Pack is the price of one pack. Pack Size and Pack Unit give the Price per Unit used to compare."),
        ("5", "Keep the same Pack Unit for an item every time (e.g. always oz for cereal) so prices compare correctly."),
        (None, None),
        ("Good to know", None),
        ("By weight", "Meat and bananas are charged by weight; their pack sizes are estimates until the receipt."),
        ("Cart prices", "Rows logged from a cart use the cart price that day. Update them from the receipt if they change."),
    ]
    for i, (a, b) in enumerate(lines, start=3):
        rm[f"A{i}"].value = a
        rm[f"A{i}"].font = f_bold if b is None or i <= 8 else f_base
        rm[f"B{i}"].value = b
        rm[f"B{i}"].font = f_base
        rm[f"B{i}"].alignment = Alignment(wrap_text=True, vertical="top")
        if a == "Blue text":
            rm[f"A{i}"].font = f_input
        if a == "Yellow fill":
            rm[f"A{i}"].fill = INPUT_FILL
    rm.column_dimensions["A"].width = 30
    rm.column_dimensions["B"].width = 110


# ---------------------------------------------------------------- upsert
def upsert(path, data_path):
    with open(data_path) as fh:
        data = json.load(fh)
    wb = load_workbook(path)
    log, chk, cat, orders = wb[LOG], wb[CHECKS], wb[CAT], wb[ORDERS]
    sl, sc, sk, so = SHEETS[LOG], SHEETS[CHECKS], SHEETS[CAT], SHEETS[ORDERS]

    catalog = {norm(cat[f"A{r}"].value): r for r in range(2, next_empty_row(cat, sk))}
    units = {k: cat[f"C{r}"].value for k, r in catalog.items()}

    # Validate everything first so a bad record never leaves a half-written workbook.
    errors, warnings = [], []
    new_items = {norm(c["item"]) for c in data.get("catalog", [])}
    for i, p in enumerate(data.get("purchases", [])):
        missing = [f for f in ("date", "store", "item", "product", "pack_size", "pack_unit", "qty", "price")
                   if p.get(f) in (None, "")]
        if missing:
            errors.append(f"purchase {i} ({p.get('product')}): missing {', '.join(missing)}")
        k = norm(p.get("item"))
        if k and k not in catalog and k not in new_items and not p.get("category"):
            errors.append(f"purchase {i}: item '{p.get('item')}' is not in Item Catalog; "
                          "add it under 'catalog' or give the purchase a 'category'")
    for i, c in enumerate(data.get("price_checks", [])):
        missing = [f for f in ("date", "store", "item", "product", "pack_size", "pack_unit", "price")
                   if c.get(f) in (None, "")]
        if missing:
            errors.append(f"price check {i} ({c.get('product')}): missing {', '.join(missing)}")
    for i, o in enumerate(data.get("orders", [])):
        if not o.get("date") or not o.get("store"):
            errors.append(f"order {i}: needs date and store")
    if errors:
        sys.exit("Nothing written:\n  " + "\n  ".join(errors))

    counts = {"catalog added": 0, "catalog updated": 0, "purchases added": 0, "purchases updated": 0,
              "price checks added": 0, "price checks updated": 0, "orders added": 0, "orders updated": 0}

    def upsert_catalog(rec):
        k = norm(rec["item"])
        if k in catalog:
            write_fields(cat, sk, catalog[k], rec)
            counts["catalog updated"] += 1
        else:
            r = next_empty_row(cat, sk)
            write_fields(cat, sk, r, rec)
            catalog[k] = r
            counts["catalog added"] += 1
        if rec.get("unit"):
            units[k] = rec["unit"]

    for rec in data.get("catalog", []):
        upsert_catalog(rec)

    existing = rows_by_key(log, sl, lambda ws, r: line_key(ws[f"A{r}"].value, ws[f"B{r}"].value,
                                                           ws[f"H{r}"].value, ws[f"F{r}"].value))
    for p in data.get("purchases", []):
        k = norm(p["item"])
        if k not in catalog:
            upsert_catalog({"item": p["item"], "category": p["category"], "unit": p["pack_unit"],
                            "preferred_store": p["store"]})
        if units.get(k) and norm(units[k]) != norm(p["pack_unit"]):
            warnings.append(f"{p['product']}: pack unit '{p['pack_unit']}' differs from catalog unit "
                            f"'{units[k]}' for {p['item']}, so price per unit won't compare")
        key = line_key(p["date"], p["store"], p.get("sku"), p["product"])
        if key in existing:
            write_fields(log, sl, existing[key][0], p)
            counts["purchases updated"] += 1
        else:
            r = next_empty_row(log, sl)
            write_fields(log, sl, r, p)
            existing[key] = [r]
            counts["purchases added"] += 1

    existing = rows_by_key(chk, sc, lambda ws, r: line_key(ws[f"A{r}"].value, ws[f"B{r}"].value,
                                                           ws[f"E{r}"].value, ws[f"D{r}"].value))
    for c in data.get("price_checks", []):
        k = norm(c["item"])
        if units.get(k) and norm(units[k]) != norm(c["pack_unit"]):
            warnings.append(f"price check {c['product']}: pack unit '{c['pack_unit']}' differs from "
                            f"catalog unit '{units[k]}'")
        key = line_key(c["date"], c["store"], c.get("sku"), c["product"])
        if key in existing:
            write_fields(chk, sc, existing[key][0], c)
            counts["price checks updated"] += 1
        else:
            r = next_empty_row(chk, sc)
            write_fields(chk, sc, r, c)
            existing[key] = [r]
            counts["price checks added"] += 1

    for o in data.get("orders", []):
        d, s, num = str(to_date(o["date"])), norm(o["store"]), norm(o.get("order_number"))
        candidates = [r for r in range(2, next_empty_row(orders, so))
                      if str(to_date(orders[f"A{r}"].value)) == d and norm(orders[f"B{r}"].value) == s]
        match = None
        if num:
            match = next((r for r in candidates if norm(orders[f"C{r}"].value) == num), None)
            match = match or next((r for r in candidates if not norm(orders[f"C{r}"].value)), None)
        elif candidates:
            match = candidates[0]
        if match:
            write_fields(orders, so, match, o)
            counts["orders updated"] += 1
        else:
            write_fields(orders, so, next_empty_row(orders, so), o)
            counts["orders added"] += 1

    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    wb.save(path)
    print(json.dumps({"saved": path, **{k: v for k, v in counts.items() if v}, "warnings": warnings}, indent=2))


# ---------------------------------------------------------------- read-only reports
def _rows(ws, spec, fields):
    out = []
    for r in range(2, next_empty_row(ws, spec)):
        out.append({f: ws[f"{spec['inputs'][f]}{r}"].value for f in fields})
    return out


def _ppu(rec):
    try:
        return round(float(rec["price"]) / float(rec["pack_size"]), 4)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def catalog_report(path):
    wb = load_workbook(path)
    cat_rows = _rows(wb[CAT], SHEETS[CAT], ["item", "category", "unit", "usual_amount", "preferred_store",
                                            "on_hand", "reorder_at", "notes"])
    buys = _rows(wb[LOG], SHEETS[LOG], ["date", "store", "item", "product", "sku", "pack_size", "pack_unit",
                                        "qty", "price"])
    checks = _rows(wb[CHECKS], SHEETS[CHECKS], ["date", "store", "item", "product", "sku", "pack_size",
                                                "pack_unit", "price"])
    report = []
    for c in cat_rows:
        k = norm(c["item"])
        mine = sorted((b for b in buys if norm(b["item"]) == k), key=lambda b: str(to_date(b["date"])))
        seen = [dict(x, source="bought") for x in mine] + \
               [dict(x, source="price check") for x in checks if norm(x["item"]) == k]
        # Only compare rows in the catalog's unit; a per-box price can't be ranked against per-oz.
        priced = [x for x in seen if _ppu(x) is not None
                  and (not c["unit"] or norm(x["pack_unit"]) == norm(c["unit"]))]
        best = min(priced, key=_ppu) if priced else None
        latest_by_store = {}
        for x in sorted(priced, key=lambda x: str(to_date(x["date"]))):
            latest_by_store[x["store"]] = {"date": str(to_date(x["date"])), "product": x["product"],
                                           "sku": x["sku"], "price": x["price"], "pack_size": x["pack_size"],
                                           "price_per_unit": _ppu(x), "source": x["source"]}
        last = mine[-1] if mine else None
        report.append({
            **{f: c[f] for f in c},
            "times_bought": len(mine),
            "last_bought": None if not last else {"date": str(to_date(last["date"])), "store": last["store"],
                                                  "product": last["product"], "sku": last["sku"],
                                                  "qty": last["qty"], "price": last["price"]},
            "latest_price_by_store": latest_by_store,
            "best_price_per_unit": None if not best else {"store": best["store"], "product": best["product"],
                                                          "price_per_unit": _ppu(best),
                                                          "date": str(to_date(best["date"]))},
            "needs_reorder": (c["on_hand"] is not None and c["reorder_at"] is not None
                              and c["on_hand"] <= c["reorder_at"]),
        })
    print(json.dumps(report, indent=2, default=str))


def summary_report(path, date):
    d = str(to_date(date))
    wb = load_workbook(path)
    buys = [b for b in _rows(wb[LOG], SHEETS[LOG], ["date", "store", "qty", "price", "regular_price"])
            if str(to_date(b["date"])) == d]
    ords = [o for o in _rows(wb[ORDERS], SHEETS[ORDERS], ["date", "store", "order_number", "fees", "tip",
                                                          "tax", "status"])
            if str(to_date(o["date"])) == d]
    out = {}
    for store in sorted({b["store"] for b in buys} | {o["store"] for o in ords}):
        sb = [b for b in buys if b["store"] == store]
        so = [o for o in ords if o["store"] == store]
        subtotal = round(sum(b["qty"] * b["price"] for b in sb), 2)
        extra = round(sum((o["fees"] or 0) + (o["tip"] or 0) + (o["tax"] or 0) for o in so), 2)
        out[store] = {"lines": len(sb), "packs": sum(b["qty"] for b in sb), "subtotal": subtotal,
                      "savings": round(sum((b["regular_price"] - b["price"]) * b["qty"]
                                           for b in sb if b["regular_price"]), 2),
                      "fees_tip_tax": extra, "total": round(subtotal + extra, 2),
                      "orders": [{k: o[k] for k in ("order_number", "status")} for o in so]}
    out["all_stores_total"] = round(sum(v["total"] for v in out.values()), 2)
    print(json.dumps({"date": d, **out}, indent=2, default=str))


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    if cmd == "init" and len(args) == 1:
        init(args[0])
    elif cmd == "upsert" and len(args) == 2:
        upsert(*args)
    elif cmd == "catalog" and len(args) == 1:
        catalog_report(args[0])
    elif cmd == "summary" and len(args) == 2:
        summary_report(*args)
    else:
        sys.exit(__doc__)
