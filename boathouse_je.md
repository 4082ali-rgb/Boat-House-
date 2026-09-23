# Boathouse Daily Revenue JE — Claude Code Instructions

You are processing a **Manning Park Resort Boathouse** daily "Sales Overview" PDF (Clover POS)
into a QuickBooks Online (QBO) journal-entry import CSV. Follow this exactly, the same way
Imran and Claude have been doing it manually. If anything is ambiguous or missing, **stop and
ask Imran** rather than guessing — see "When to ask" at the bottom.

## 0. Inputs

- One or more Boathouse "Sales Overview" PDFs (filename pattern:
  `Manning_Park_Boathouse-Sales_Overview_YYYY-MM-DD.pdf`), each covering a single business day.
- Each PDF has two parts: a Clover "Sales Overview" report (Gross Sales, Discounts, Refunds,
  Tender Types, Revenue Classes, Card Types, Cash Collected) and a "Tax details" report
  (GST/PST applicable sales, taxes collected).
- Class code for every line: **0040-BOAT HOUSE** (fixed, never varies).

## 1. Extract these figures from the PDF

From the **Sales Overview** section:
- Tender Types table → Credit Card, Debit Card, Cash sales totals (use these three; ignore
  "Amount Collected" column per tender, use "Sales Total")
- Revenue Classes table → each category's **Gross** and **Discount** columns (not Net — see
  discount handling below)
- Tips (top summary line)
- Card Types table → Visa / MasterCard / Interac sales totals

From the **Tax details** section:
- GST (5%) "Taxes collected"
- PST (7%) "Taxes collected"
- Always use the Tax Details table's figures, not the per-category tax column in Revenue
  Classes, even if they differ by a cent — Tax Details is the source of truth.

## 2. Card tender reconciliation rule

Check whether **Card Types total** (Visa + MasterCard + Interac) equals **Tender Types**
(Credit Card + Debit Card) combined:

- **If they match**: post the card portion of 1007 split by brand (Visa / MasterCard /
  Debit), one line each, using the Card Types amounts. Interac maps to "Debit" in the
  description.
- **If they don't reconcile**: do NOT split by brand. Post a single 1007 line for the combined
  Credit Card + Debit Card total instead, and flag the mismatch in the Issues section.

Cash → separate line to **1002 Petty Cash in safe**, using the Tender Types Cash figure. If
Cash is $0.00 or absent, omit the 1002 line entirely (do not post a $0 line).

## 3. Revenue class → GL account mapping (Boathouse)

| Clover Revenue Class | QBO Account |
|---|---|
| Boat Rental | 3032 Boat House Rental |
| Ice Cream | 3007 Revenue - Miscellaneous |
| Non-Alcoholic | 3006 Revenue - Non-Alcoholic |
| Seasonal | 3021 Revenue - Miscellaneous Retail |
| Snacks | 3014 Revenue - Snacks |
| Gifts | 3018 Revenue - Souvenir |
| Unclassified | 3029 Miscellaneous Revenue |

Only include a category's line if that category appears in the Revenue Classes table for
that day (nonzero net sold). Never post a $0.00 line for a category that didn't sell.

**If a new/unrecognized revenue class appears that isn't in this table, STOP and ask Imran**
which GL account to use before finalizing the entry. Do not guess.

## 4. Discount handling

If the Discounts column is nonzero for the day (top summary or a specific Revenue Class row):

- Post the affected revenue category at its **Gross** amount (not net) on its normal GL line.
- Add a separate debit line: **3050 Discounts given**, amount = the discount amount (as a
  positive debit).
- This nets the entry to the same total as if you'd posted net sales, but keeps discounts
  visible as their own GL line, per current convention.

## 5. Fixed lines (always, regardless of category mix)

- **GST**: credit 2029 GST Charged on Sales
- **PST**: credit 2035 PST 7% Charged on Sales
- **Tips**: credit 6044 Tips & Gratuities (current interim treatment — known
  misclassification vs. Tips Payable, but this is the standing convention until a batch
  correction is made; do not change this without Imran's explicit instruction)

## 6. Row construction

Debit side: 1007 (split or combined per §2), 1002 Petty Cash (if cash > 0), 3050 Discounts
given (if any discount).

Credit side: one line per revenue category actually sold, GST, PST, Tips.

**Balance check**: Debits must equal Credits exactly (to the penny) before writing the file.
If they don't balance, do not deliver the CSV — find the discrepancy and either fix it or ask
Imran; state clearly in the response that the entry does not balance and why.

## 7. CSV format (QBO import)

Columns, in order:
```
*JournalNo,*JournalDate,Memo,*AccountName,Debits,Credits,Description,Name,Location,Class
```

- `*JournalNo` and `*JournalDate` and `Memo` repeat identically on every row.
- `*JournalDate` format: `DD-MM-YYYY`
- `Memo` = `Boathouse Daily Revenue {Month} {DD} {YYYY}` (e.g. `Boathouse Daily Revenue Aug 14 2026`)
- `Description` = for lines that share an account across multiple rows (i.e. the 1007 split
  lines, and any revenue category that could repeat), prefix with the category/tender name
  and a dash: `{label}-Boathouse Daily Revenue {Month} {DD} {YYYY}` (e.g.
  `MasterCard-Boathouse Daily Revenue Aug 14 2026`, `Ice Cream-Boathouse Daily Revenue Aug 14
  2026`). For single-occurrence accounts (GST, PST, Tips, Petty Cash, Discounts) use plain
  `Boathouse Daily Revenue {Month} {DD} {YYYY}` with no prefix. In practice always prefix
  per-category revenue lines since Ice Cream/3007 recurs across days but is single-occurrence
  within a day — use the category label on every revenue line and tender-brand label on every
  1007 line.
- `Class` = `0040-BOAT HOUSE` on every row.
- `Name` and `Location` = blank.
- **No commas** anywhere in free text — reword instead of relying on CSV quoting.
- Line endings must be **CRLF** (`\r\n`), not LF. When writing with Python, use
  `csv.writer(f, lineterminator='\r\n')`.
- One amount per row goes in either Debits or Credits, never both; the other is blank.

## 8. Journal numbers

- Boathouse does not strictly auto-increment. Default behavior:
  - Look at the last known Boathouse journal number (ask Imran or check for a running log/prior
    CSVs in the working folder if available).
  - If processing multiple consecutive days in one run with no gaps, increment by 1 per day
    and state each number used.
  - If there's any gap in the day sequence, or Imran has just given an explicit new number,
    **stop incrementing on your own assumption — confirm the next number with Imran** before
    finalizing that entry.
- If Imran supplies an explicit journal number for a given date, always use it and treat it as
  a new anchor point for subsequent auto-increment.

## 9. Output

- Save each day as its own CSV: `JJ####_Boathouse_{Month}{DD}_{YYYY}.csv` in the working/output
  folder.
- Never batch multiple days into one file — one file per day, one JE per file.
- Once a CSV has been delivered/saved, do not regenerate it for corrections — Imran adjusts
  directly in QBO. Only rebuild if explicitly asked or if it's a new entry.

## 10. Response format after each day

After building and saving the CSV, always respond with:
1. One-line balance confirmation (total debits = total credits = $X.XX).
2. A **Flags/Issues** section (always include this section, even if short) covering:
   - Any category new/changed vs. recent days
   - Any discount, refund, or unusual tender mix
   - Any card reconciliation mismatch
   - Any zero-cash or zero-card day
   - Anything that required a guess or assumption

## When to ask Imran (do not guess on these)

- An unrecognized Revenue Class not in the §3 table
- Card Types total doesn't reconcile to Tender Types and it's unclear how to split
- A gap in the journal number sequence
- Any GST/PST rate or tax structure that doesn't match the standard 5%/7% pattern
- Any refund, chargeback, or negative-net-sales day
- Anything that would cause the entry not to balance
- Multiple PDFs given for the same date, or a PDF whose internal date range doesn't match its
  filename

When you do ask, ask a specific, single question — don't pause the whole batch for one
uncertain day; keep going on the days that are clear and flag the one that needs input.
