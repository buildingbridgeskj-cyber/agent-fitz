#!/usr/bin/env bash
# Agent Fitz Week 7: separate paper-ledger runs for four college football prop groups.
# These boards are October 16 research snapshots, NOT a real-time sportsbook feed.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
PROP_GROUPS=(passing rushing receiving touchdown)
if [[ ${1:-all} != "all" ]]; then
  case "$1" in
    passing|rushing|receiving|touchdown) PROP_GROUPS=("$1") ;;
    *) echo "Usage: bash run_week7_props.sh [passing|rushing|receiving|touchdown|all]" >&2; exit 2 ;;
  esac
fi

echo "Fitz — Saturday Oct 17, 2026 | Week 7 college football"
echo "PUBLIC RESEARCH SNAPSHOTS ONLY — recheck live lines/players before decisions."
for group in "${PROP_GROUPS[@]}"; do
  board="boards/agent_fitz_week7_${group}_props_2026.json"
  ledger="data/agent_fitz_week7_${group}.sqlite3"
  printf '\n========== %s ==========' "${group^^}"
  printf '\n'
  python agent_fitz.py freeze --board "$board" --db "$ledger" --append
  echo
  echo "Full board (including watch-only/PASS candidates):"
  python agent_fitz.py board --season 2026 --week 7 --db "$ledger"
  echo
  echo "Market snapshot: direction, yard/reception threshold, listed odds and status"
  python - "$board" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    picks = json.load(f)["picks"]
for p in sorted(picks, key=lambda x: -int(x["score"])):
    odds = p.get("odds") or "not verified"
    print(f'{p["score"]:>3} {p["market"]:<12} {p["selection"]:<48} odds {odds:<13} {p["status"]}')
PY
done
echo
echo "Done. Each category uses its OWN ledger, so spread and prop tickets do not mix."
echo "Fewer than 3 independent qualified candidates means no 3-, 5-, or 8-leg card for that category."
