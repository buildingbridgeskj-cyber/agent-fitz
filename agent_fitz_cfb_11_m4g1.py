#!/usr/bin/env python3
"""Agent Fitz: college-football paper analysis and frozen-ticket ledger."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_DEFAULT = "agent_fitz.sqlite3"
MIN_SCORE = 70
CARD_SIZES = (3, 5, 8)


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
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
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"matchup", "market", "selection", "line", "score", "reason", "source"}
    for i, pick in enumerate(data["picks"], 1):
        missing = required - pick.keys()
        if missing:
            raise ValueError(f"Pick {i} missing: {', '.join(sorted(missing))}")
    return data


def allocate_cards(picks):
    qualified = [p for p in picks if int(p["score"]) >= MIN_SCORE]
    qualified.sort(key=lambda p: (-int(p["score"]), p["matchup"], p["selection"]))
    cards = {}
    for size in CARD_SIZES:
        # Each ticket is built independently from the best available picks.
        # Strong selections may intentionally be reused on larger tickets.
        cards[size] = qualified[:size] if len(qualified) >= size else []
    return cards


def freeze(con, board, append=False):
    season, week = int(board["season"]), int(board["week"])
    existing = con.execute(
        "SELECT COUNT(*) n FROM picks WHERE season=? AND week=?", (season, week)
    ).fetchone()["n"]
    if existing and not append:
        raise SystemExit("Week already frozen. Use --append to add only new selections.")
    cards = allocate_cards(board["picks"])
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
    for r in rows:
        result = r["result"] or "OPEN"
        print(f"{r['score']:>3} {r['tier']:<11} {r['selection']:<22} "
              f"{r['matchup']:<34} {result}")


def grade(con, season, week, results_path):
    data = json.loads(Path(results_path).read_text(encoding="utf-8"))
    updated = 0
    for x in data["results"]:
        cur = con.execute(
            """UPDATE picks SET result=?, actual=?
               WHERE season=? AND week=? AND matchup=? AND market=? AND selection=?""",
            (x["result"].upper(), x.get("actual"), season, week,
             x["matchup"], x["market"], x["selection"]),
        )
        updated += cur.rowcount
    con.commit()
    print(f"Graded {updated} selections.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB_DEFAULT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--board", required=True)
    f.add_argument("--append", action="store_true")
    for name in ("cards", "board"):
        p = sub.add_parser(name)
        p.add_argument("--season", type=int, required=True)
        p.add_argument("--week", type=int, required=True)
    g = sub.add_parser("grade")
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
