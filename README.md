# Boathouse Daily Revenue JE Automation

Two files:

- **`boathouse_je.md`** — the full instructions Claude Code should follow: how to read the
  Clover Sales Overview PDF, the GL mapping table, discount handling, card reconciliation
  rule, CSV format, journal number rules, and — critically — when to stop and ask Imran
  instead of guessing.
- **`build_boathouse_je.py`** — a Python helper that takes the figures already pulled from
  the PDF and builds the balanced, correctly-formatted CSV. It also runs the balance check
  and refuses to write a file that doesn't balance to the penny.

## How to use this with Claude Code

1. Drop `boathouse_je.md` somewhere Claude Code can read it (e.g. as a custom slash command
   `/boathouse-je`, or just point Claude Code at it: "follow the instructions in
   boathouse_je.md").
2. Give Claude Code the day's PDF(s).
3. Claude Code should:
   - Read the PDF (Tender Types, Revenue Classes, Card Types, Tax Details, Tips).
   - Build a `data` dict matching the shape documented in `build_boathouse_je.py`.
   - Call `build_entry(data)`.
   - Report back the balance confirmation and the Flags/Issues section as described in
     `boathouse_je.md` §10.
4. If Claude Code hits any of the "When to ask" conditions in `boathouse_je.md`, it should
   stop and ask you directly rather than guessing — this is by design, not a bug.

## Known gaps / things to keep an eye on early on

- The GL mapping table only covers the 7 revenue categories seen so far (Boat Rental, Ice
  Cream, Non-Alcoholic, Seasonal, Snacks, Gifts, Unclassified). If Clover adds a new category
  next season, Claude Code will stop and ask rather than invent a mapping.
- Journal number auto-increment logic is deliberately conservative — it will ask rather than
  assume across gaps. You can tighten this once you're comfortable trusting it more.
- This only covers Boathouse. The other outlets (Pinewoods, Country Store, Skyview, etc.)
  have their own conventions already recorded separately — this script is not meant to be
  reused for them as-is.
