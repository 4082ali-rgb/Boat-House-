#!/usr/bin/env python3
"""
build_boathouse_je.py

Builds a QBO-import-ready journal entry CSV for a single Boathouse daily
revenue entry, given the figures already extracted from the Clover Sales
Overview PDF by Claude Code.

This script does NOT read PDFs. Claude Code should read the PDF, pull out
the figures below (see the `example` dict for the exact shape), and either
call `build_entry(...)` directly from another script/REPL, or edit the
`DATA` dict at the bottom and run this file directly for one day at a time.

Usage (edit-and-run style):
    python3 build_boathouse_je.py

Or import and call:
    from build_boathouse_je import build_entry
    build_entry(DATA)
"""

import csv
import sys
from datetime import datetime

CLASS_CODE = "0040-BOAT HOUSE"

# Revenue class -> QBO account name (must match Chart of Accounts exactly)
REVENUE_MAP = {
    "Boat Rental": "3032 Boat House Rental",
    "Ice Cream": "3007 Revenue - Miscellaneous",
    "Non-Alcoholic": "3006 Revenue - Non-Alcoholic",
    "Seasonal": "3021 Revenue - Miscellaneous Retail",
    "Snacks": "3014 Revenue - Snacks",
    "Gifts": "3018 Revenue - Souvenir",
    "Unclassified": "3029 Miscellaneous Revenue",
}

CARD_ACCOUNT = "1007 Visa / Mstrcrd / Debit Receivable"
CASH_ACCOUNT = "1002 Petty Cash in safe"
DISCOUNT_ACCOUNT = "3050 Discounts given"
GST_ACCOUNT = "2029 GST Charged on Sales"
PST_ACCOUNT = "2035 PST 7% Charged on Sales"
TIPS_ACCOUNT = "6044 Tips & Gratuities"


def build_entry(data, out_dir="/mnt/user-data/outputs"):
    """
    data = {
        "journal_no": "JJ3370",
        "date": "2026-09-01",          # ISO format, will be reformatted
        "cards": {"Visa": 100.00, "MasterCard": 50.00, "Interac": 25.00},
            # OR if card types don't reconcile to tender types:
            # "cards_combined": 175.00   (use instead of "cards")
        "cash": 10.00,                 # 0 or omit if no cash
        "revenue": {                   # only categories actually sold
            "Boat Rental": {"gross": 500.00, "discount": 0.00},
            "Ice Cream": {"gross": 20.00, "discount": 0.00},
        },
        "gst": 25.00,
        "pst": 33.00,
        "tips": 40.00,
    }
    """
    dt = datetime.strptime(data["date"], "%Y-%m-%d")
    date_str = dt.strftime("%d-%m-%Y")
    memo_date = dt.strftime("%b %-d %Y") if sys.platform != "win32" else dt.strftime("%b %#d %Y")
    memo = f"Boathouse Daily Revenue {memo_date}"
    jn = data["journal_no"]

    rows = []

    def add(account, debit=None, credit=None, desc_prefix=None):
        desc = f"{desc_prefix}-{memo}" if desc_prefix else memo
        rows.append({
            "*JournalNo": jn,
            "*JournalDate": date_str,
            "Memo": memo,
            "*AccountName": account,
            "Debits": f"{debit:.2f}" if debit is not None else "",
            "Credits": f"{credit:.2f}" if credit is not None else "",
            "Description": desc,
            "Name": "",
            "Location": "",
            "Class": CLASS_CODE,
        })

    # --- Debit side: card receivable ---
    # Description label: Interac tender is labeled "Debit" in the JE per convention
    LABEL_OVERRIDES = {"Interac": "Debit"}

    if "cards_combined" in data:
        add(CARD_ACCOUNT, debit=data["cards_combined"])
    else:
        for brand, amt in data.get("cards", {}).items():
            if amt:
                label = LABEL_OVERRIDES.get(brand, brand)
                add(CARD_ACCOUNT, debit=amt, desc_prefix=label)

    # --- Debit side: cash ---
    if data.get("cash"):
        add(CASH_ACCOUNT, debit=data["cash"])

    # --- Debit side: discounts (sum of all category discounts) ---
    total_discount = sum(v.get("discount", 0) for v in data.get("revenue", {}).values())
    if total_discount:
        add(DISCOUNT_ACCOUNT, debit=round(total_discount, 2))

    # --- Credit side: revenue categories (posted at GROSS) ---
    for category, vals in data.get("revenue", {}).items():
        if category not in REVENUE_MAP:
            raise ValueError(
                f"Unrecognized revenue category '{category}' — ask Imran which GL "
                f"account to use before proceeding."
            )
        gross = vals.get("gross", 0)
        if gross:
            add(REVENUE_MAP[category], credit=gross, desc_prefix=category)

    # --- Credit side: tax and tips ---
    if data.get("gst"):
        add(GST_ACCOUNT, credit=data["gst"])
    if data.get("pst"):
        add(PST_ACCOUNT, credit=data["pst"])
    if data.get("tips"):
        add(TIPS_ACCOUNT, credit=data["tips"])

    # --- Balance check ---
    total_debits = sum(float(r["Debits"]) for r in rows if r["Debits"])
    total_credits = sum(float(r["Credits"]) for r in rows if r["Credits"])
    if round(total_debits - total_credits, 2) != 0:
        raise ValueError(
            f"ENTRY DOES NOT BALANCE: Debits {total_debits:.2f} vs Credits "
            f"{total_credits:.2f} (diff {total_debits - total_credits:.2f}). "
            f"Do not deliver this CSV — find the discrepancy or ask Imran."
        )

    # --- Write CSV ---
    fname = f"{jn}_Boathouse_{dt.strftime('%b%d_%Y')}.csv"
    out_path = f"{out_dir}/{fname}"
    fieldnames = ["*JournalNo", "*JournalDate", "Memo", "*AccountName",
                  "Debits", "Credits", "Description", "Name", "Location", "Class"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {out_path}")
    print(f"Balanced at ${total_debits:.2f}")
    return out_path, total_debits


# ---------------------------------------------------------------------------
# Example / edit-and-run block
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    DATA = {
        "journal_no": "JJ0000",
        "date": "2026-01-01",
        "cards": {"Visa": 0.00, "MasterCard": 0.00, "Interac": 0.00},
        "cash": 0.00,
        "revenue": {
            "Boat Rental": {"gross": 0.00, "discount": 0.00},
        },
        "gst": 0.00,
        "pst": 0.00,
        "tips": 0.00,
    }
    print("This is a template — edit DATA above (or import build_entry) before running for real.")
    # build_entry(DATA)
