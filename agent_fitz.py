#!/usr/bin/env python3
"""Agent Fitz: college-football paper analysis and frozen-ticket ledger.

Paper analysis only. Never connects to a sportsbook or places wagers.
Workflow: freeze a week's board -> review cards -> grade results after games.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_DEFAULT = "agent_fitz.sqlite3"
MIN_SCORE = 70
CARD_SIZES = (3, 5, 8)
VALID_RESULTS = ("WIN", "LOSS", "PUSH", "VOID")


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    # NOTE: card_size is retained for compatibility with existing databases
    # but is currently unused; cards are always recomputed from scores.
    con.execute("""
        CREATE TABLE IF NOT EXISTS picks (
          season INTEGER NOT NULL, week INTEGER NOT NULL,
          captured_at TEXT NOT NULL, matchup TEXT NOT NULL,
          market TEXT NOT NULL, selection TEXT NOT NULL,
          line REAL, score INTEGER NOT NULL, tier TEXT NOT NULL,
          reason TEXT, source TEXT, card_size INTEGER,
          result TEXT, actual TEXT,
          PRIMARY KEY (season, week, matchup, market, selection)
        )
    """)
    con.commit()
    return con


def tier(score):
    if score >= 90: return "ELITE"
    if score >= 85: return "VERY STRONG"
    if score >= 80: return "STRONG"
    if score >= 75: return "GOOD"
    if score >= 70: return "QUALIFIED"
    return "PASS"


def load_board(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Board file not found: {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Board file is not valid JSON: {e}")
    for key in ("season", "week", "picks"):
        if key not in data:
            raise SystemExit(f"Board file missing required key: {key!r}")
    required = {"matchup", "market", "selection", "line", "score", "reason", "source"}
    for i, pick in enumerate(data["picks"], 1):
        missing = required - pick.keys()
        if missing:
            raise SystemExit(f"Pick {i} missing: {', '.join(sorted(missing))}")
        try:
            int(pick["score"])
        except (TypeError, ValueError):
            raise SystemExit(f"Pick {i} has non-numeric score: {pick['score']!r}")
    return data


def allocate_cards(picks):
    qualified = [p for p in picks if int(p["score"]) >= MIN_SCORE]
    qualified.sort(key=lambda p: (-int(p["score"]), p["matchup"], p["selection"]))
    cards = {}
    for size in CARD_SIZES:
        # Each ticket is built independently from the best available picks.
        # Because every card takes the top-N, smaller cards are always a
        # subset of larger ones: the 5-leg contains the 3-leg core, and the
        # 8-leg contains the 5-leg core.
        cards[size] = qualified[:size] if len(qualified) >= size else []
    return cards


def freeze(con, board, append=False):
    season, week = int(board["season"]), int(board["week"])
    if not board["picks"]:
        raise SystemExit("Board has no picks; nothing to freeze.")
    existing = con.execute(
        "SELECT COUNT(*) n FROM picks WHERE season=? AND week=?", (season, week)
    ).fetchone()["n"]
    if existing and not append:
        raise SystemExit("Week already frozen. Use --append to add only new selections.")
    captured = datetime.now().astimezone().isoformat(timespec="seconds")
    added = 0
    for p in board["picks"]:
        score = int(p["score"])
        key = (p["matchup"], p["market"], p["selection"])
        cur = con.execute(
            """INSERT OR IGNORE INTO picks
               (season,week,captured_at,matchup,market,selection,line,score,tier,
                reason,source,card_size)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (season, week, captured, *key, p.get("line"), score, tier(score),
             p.get("reason", ""), p.get("source", ""), None),
        )
        added += cur.rowcount
    con.commit()
    print(f"Frozen {added} new selections for {season} Week {week}.")
    show_cards(con, season, week)


def show_cards(con, season, week):
    rows = con.execute(
        """SELECT * FROM picks WHERE season=? AND week=? AND score>=?
           ORDER BY score DESC, matchup, selection""", (season, week, MIN_SCORE)
    ).fetchall()
    if not rows:
        print("No qualified frozen cards.")
        return
    cards = allocate_cards([dict(r) for r in rows])
    for size in CARD_SIZES:
        card = cards[size]
        print(f"\n{size}-LEG PAPER TICKET")
        print("-" * 72)
        if len(card) != size:
            print("PASS — insufficient diversified qualifiers")
            continue
        for r in card:
            line = "" if r["line"] is None else f" {r['line']:+g}"
            print(f"{r['selection']}{line} | {r['matchup']} | {r['score']} {r['tier']}")


def board(con, season, week):
    rows = con.execute(
        "SELECT * FROM picks WHERE season=? AND week=? ORDER BY score DESC, matchup",
        (season, week),
    ).fetchall()
    if not rows:
        print(f"No frozen picks for {season} Week {week}.")
        return
    for r in rows:
        result = r["result"] or "OPEN"
        print(f"{r['score']:>3} {r['tier']:<11} {r['selection']:<22} "
              f"{r['matchup']:<34} {result}")


def grade(con, season, week, results_path):
    try:
        data = json.loads(Path(results_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Results file not found: {results_path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Results file is not valid JSON: {e}")
    if "results" not in data:
        raise SystemExit("Results file missing required key: 'results'")
    updated = 0
    unmatched = []
    for x in data["results"]:
        for key in ("matchup", "market", "selection"):
            if key not in x:
                raise SystemExit(f"Result entry missing required key: {key!r}")
        result = str(x.get("result", "")).upper().strip()
        if result not in VALID_RESULTS:
            raise SystemExit(
                f"Invalid result {x.get('result')!r} for {x.get('matchup')!r}; "
                f"must be one of: {', '.join(VALID_RESULTS)}"
            )
        cur = con.execute(
            """UPDATE picks SET result=?, actual=?
               WHERE season=? AND week=? AND matchup=? AND market=? AND selection=?""",
            (result, x.get("actual"), season, week,
             x["matchup"], x["market"], x["selection"]),
        )
        if cur.rowcount:
            updated += cur.rowcount
        else:
            unmatched.append(x["matchup"])
    con.commit()
    print(f"Graded {updated} selections.")
    if unmatched:
        print(f"WARNING: {len(unmatched)} result(s) matched no frozen pick "
              f"(check matchup/market/selection spelling):")
        for m in unmatched:
            print(f"  - {m}")
    rows = con.execute(
        """SELECT result, COUNT(*) n FROM picks
           WHERE season=? AND week=? AND result IS NOT NULL GROUP BY result""",
        (season, week),
    ).fetchall()
    if rows:
        print("Record: " + ", ".join(f"{r['result']} {r['n']}" for r in rows))


def main():
    ap = argparse.ArgumentParser(description="Agent Fitz: CFB paper tickets and grading ledger.")
    ap.add_argument("--db", default=DB_DEFAULT,
                    help="Ledger database path (also accepted after the subcommand).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # --db is accepted both globally and per-subcommand for convenience.
    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument("--db", default=DB_DEFAULT)

    f = sub.add_parser("freeze", parents=[db_parent],
                       help="Freeze a week's board into the ledger.")
    f.add_argument("--board", required=True)
    f.add_argument("--append", action="store_true",
                   help="Add only new selections to an already-frozen week.")
    for name in ("cards", "board"):
        p = sub.add_parser(name, parents=[db_parent])
        p.add_argument("--season", type=int, required=True)
        p.add_argument("--week", type=int, required=True)
    g = sub.add_parser("grade", parents=[db_parent],
                       help="Grade frozen picks from a results file.")
    g.add_argument("--season", type=int, required=True)
    g.add_argument("--week", type=int, required=True)
    g.add_argument("--results", required=True)
    args = ap.parse_args()
    con = connect(args.db)
    if args.cmd == "freeze": freeze(con, load_board(args.board), args.append)
    elif args.cmd == "cards": show_cards(con, args.season, args.week)
    elif args.cmd == "board": board(con, args.season, args.week)
    elif args.cmd == "grade": grade(con, args.season, args.week, args.results)


if __name__ == "__main__":
    main()
