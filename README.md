# Agent Fitz — College Football Paper Tickets

Paper-analysis engine for college football game lines. It never connects to
a sportsbook or places wagers. Standard library only (no dependencies).

## How it works

1. **Board** — a human-curated JSON board (`boards/`) scores each matchup 0–100
   from web research. Score ≥ 70 qualifies; below 70 is PASS.
2. **Freeze** — the week's market snapshot is frozen into `agent_fitz.sqlite3`
   before kickoff. Frozen weeks are never overwritten; `--append` adds only
   genuinely new selections.
3. **Cards** — 3-, 5-, and 8-leg paper tickets are built independently from the
   highest-rated picks. Because each card takes the top-N, strong picks are
   intentionally reused: the 5-leg contains the 3-leg core, the 8-leg contains
   the 5-leg core.
4. **Grade** — after games, a results file grades every frozen pick
   (WIN / LOSS / PUSH / VOID). Unmatched entries are reported, never silently
   dropped.

## Commands

```bash
python agent_fitz.py freeze --board boards/agent_fitz_week3_2026.json
python agent_fitz.py cards --season 2026 --week 3
python agent_fitz.py board --season 2026 --week 3
python agent_fitz.py grade --season 2026 --week 3 --results results/week3_results.json
```

If the week is already frozen and new games are added:

```bash
python agent_fitz.py freeze --board boards/agent_fitz_week3_2026.json --append
```

Use `--db path/to.db` to point at a different ledger (e.g. a scratch copy).

## Results file format

```json
{
  "season": 2026, "week": 3,
  "results": [
    {"matchup": "BYU at Colorado State", "market": "ATS",
     "selection": "BYU", "result": "WIN", "actual": "BYU 38-10"}
  ]
}
```

`matchup` / `market` / `selection` must match the frozen pick exactly;
`result` must be WIN, LOSS, PUSH, or VOID (case-insensitive).

## Rules

- Scan the full available board; never force a play.
- Freeze each week's market snapshot before kickoff.
- Never overwrite frozen prior weeks.
- Grade results after games and retain them in the ledger.
- Recheck market lines, postponements, quarterbacks, and major injury news
  before kickoff. The frozen line is the grading line; do not silently replace
  it with a later line.
