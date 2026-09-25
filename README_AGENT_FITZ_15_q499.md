# Agent Fitz — College Football

Agent Fitz is a paper-analysis engine for college football game lines. It never connects to a sportsbook or places wagers.

## Rules

- Scan the full available board; never force a play.
- Score 70 or higher to qualify; below 70 is PASS.
- Freeze each week's market snapshot before kickoff.
- Never overwrite frozen prior weeks. Use `--append` only for genuinely new selections.
- Build each 3-, 5-, and 8-leg ticket independently from the highest-rated picks.
- Strong picks may be reused across tickets: the 5-leg includes the strongest 3-leg core, and the 8-leg includes the strongest 5-leg core.
- Grade results after games and retain them in `agent_fitz.sqlite3`.
- Recheck market lines, postponements, quarterbacks, and major injury news before kickoff.

## Week 3 commands

```bash
python agent_fitz_cfb.py freeze --board agent_fitz_week3_2026.json
python agent_fitz_cfb.py cards --season 2026 --week 3
python agent_fitz_cfb.py board --season 2026 --week 3
```

If the week is already frozen and new games are added:

```bash
python agent_fitz_cfb.py freeze --board agent_fitz_week3_2026.json --append
```

The September 16 board is a provisional paper snapshot. Use the frozen line listed for grading; do not silently replace it with a later line.
