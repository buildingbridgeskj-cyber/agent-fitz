# Agent Fitz — audit & fixes (2026-09-25)

Source: Kenneth's uploaded files (`agent_fitz_cfb_11_m4g1.py`,
`agent_fitz_week3_2026_12_e0f1.json`, `AGENT_FITZ_WEEK3_TICKETS_13_yqu8.md`,
`README_AGENT_FITZ_15_q499.md`, plus two NFL DraftKings CSVs). Originals
untouched in `~/workspace/user/files/`; all work done on this copy.

## Bugs found and fixed

1. **`--db` unusable after the subcommand** — `--db` was only accepted before
   the subcommand name (`agent_fitz.py --db X freeze ...`); the natural
   `freeze --board ... --db X` errored out. Fixed: `--db` is now accepted in
   both positions via a shared parent parser.
2. **`grade()` silently dropped non-matching results** — a results entry whose
   matchup/market/selection didn't exactly match a frozen pick updated zero
   rows and printed only "Graded N selections." A typo'd team name would
   vanish without a trace. Fixed: unmatched entries are listed as a WARNING.
3. **`grade()` accepted any result string** — `"WON"`, `"win "` etc. were
   stored verbatim, corrupting the ledger. Fixed: results are normalized
   (case/whitespace) and validated against WIN / LOSS / PUSH / VOID.
4. **`load_board()` crashed with tracebacks** — missing file, invalid JSON, or
   a board missing `season`/`week`/`picks` raised raw `KeyError`/`JSONDecodeError`.
   Fixed: clear one-line errors naming the problem.
5. **Dead code in `freeze()`** — `cards = allocate_cards(board["picks"])` was
   computed and never used (cards are recomputed from the DB by `show_cards`).
   Removed.
6. **Empty-board freeze** — freezing a board with zero picks printed
   "Frozen 0 new selections" as if it worked. Now refuses with a clear message.

## Verified (not bugs)

- **Ticket construction matches the README's core-reuse claim.** `allocate_cards`
  takes the top-N independently per card size, so the 3-leg is always a subset
  of the 5-leg and the 5-leg a subset of the 8-leg. Confirmed programmatically.
- **Tickets file matches the script.** Regenerated all three Week 3 tickets from
  the JSON board through the fixed script: contents are **identical** to
  `AGENT_FITZ_WEEK3_TICKETS_13_yqu8.md`. No discrepancies.
- **Board validates cleanly** against the loader (all 16 picks have the required
  fields; scores 70–82; tiers assigned per the documented bands).
- **Timezone handling** (`captured_at`) is tz-aware local ISO — fine.
- **Schema**: `card_size` column is always NULL (cards recomputed from scores).
  Kept for compatibility with any existing `agent_fitz.sqlite3` on Kenneth's
  phone — dropping it would require a migration.

## Test results

- `py_compile` clean.
- End-to-end on a scratch DB: freeze 16 picks → re-freeze correctly refused →
  `--append` adds 0 → `cards`/`board` render → `grade` with sample results
  (mixed case results, one unmatched entry) graded 4, warned on the unmatched
  entry, and printed `Record: LOSS 1, PUSH 1, WIN 2`.
- Invalid result (`"WON"`) rejected; board missing `week` key rejected — both
  with clear messages.

## The two CSVs (NFL Thursday game)

`week3_tonight_game_lines_2026_9_uky0.csv` and
`week3_tonight_player_props_2026_10_nn7d.csv` are DraftKings snapshots for the
**NFL** Thursday game ATL @ GB (2026-09-24). The Fitz script is CFB-only and
never reads CSVs — they are orphaned inputs. They belong with the NFL side:
copies suggested for `dion-nfl-picks` under `data/nfl/`, where Agent Dion could
ingest them (its audit noted player props had no data source — the props CSV
fills exactly that gap).

## Keep / merge recommendation: **keep Fitz as its own repo**

Fitz and Cox's NCAAF coverage overlap in sport but not in design:

- **Cox** (in `dion-nfl-picks`): automated, feed-driven — pulls ESPN's NCAAF
  slate, generates model-ish parlays the same day. No human curation, no
  persistent grading ledger.
- **Fitz**: human-curated — a person scores a researched board, freezes the
  market snapshot before kickoff, builds nested paper tickets, and grades every
  pick into a SQLite ledger for a real track record.

Merging would tangle two different workflows and ledgers for little gain.
Fitz is stdlib-only, self-contained, and Kenneth already thinks of it as its
own agent. Recommended layout (implemented here):

```
agent-fitz/
  agent_fitz.py        # fixed script (renamed from agent_fitz_cfb_11_m4g1.py)
  README.md            # consolidated docs
  CHANGES.md           # this file
  .gitignore
  boards/              # weekly curated boards (JSON)
  tickets/             # generated ticket sheets (Markdown)
  results/             # results files for grading (sample included)
  data/                # ledger lives here at runtime (gitignored)
```

Suggested repo name: `agent-fitz` (private, like the dealer repo — it holds his
handicapping methodology).

## New boards archived (2026-09-25)
From Kenneth's `Agent_Fitz_2026_Week3_Complete_Markets` upload, added to `boards/`:
- `agent_fitz_week3_full_board_2026.json` — 30-game full market snapshot
- `agent_fitz_week3_td_props_2026.json` — 16 anytime-TD props (scored)
- `agent_fitz_week3_passing_props_2026.json` — 17 passing props (scored)
- `agent_fitz_props_template.json` — blank template for future weeks
- `AGENT_FITZ_WEEK3_SUMMARY.md` — "57 games | 16 qualified | 41 PASS"
The 16-pick ATS board in the upload is byte-identical in content to the
already-audited board — no new info there. The upload's sqlite (49 rows:
16 ATS + 33 props) has ZERO graded results, so nothing was imported into a
grading ledger — grades must come from real outcomes, not backfilled.
Also noted: the upload contains a variant `agent_fitz_cfb.py` (compact style,
market-group labels, INSERT OR REPLACE, stricter freeze validation). Kept the
audited `agent_fitz.py` as canonical (it has the 6 bug fixes); the variant's
ideas are documented, not merged.
