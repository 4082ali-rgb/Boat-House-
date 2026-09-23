---
description: Build a Boathouse daily revenue journal entry CSV from a Clover Sales Overview PDF
---

Follow the instructions in `boathouse_je.md` exactly, using `build_boathouse_je.py`'s
`build_entry()` to construct and write the CSV.

The user will supply one or more Boathouse "Sales Overview" PDFs (and, when relevant, a
journal number to anchor from). For each PDF:

1. Read the PDF and pull the figures per `boathouse_je.md` §1.
2. Apply the card reconciliation rule (§2), the GL mapping table (§3), and discount handling
   (§4).
3. Build a `data` dict in the shape documented in `build_boathouse_je.py`, then call
   `build_entry(data)`.
4. Respond per `boathouse_je.md` §10 — balance confirmation plus a Flags/Issues section.

If anything matches the "When to ask Imran" list at the bottom of `boathouse_je.md`, stop and
ask a specific question for that day rather than guessing, and keep going on any other days
that are clear.

$ARGUMENTS
