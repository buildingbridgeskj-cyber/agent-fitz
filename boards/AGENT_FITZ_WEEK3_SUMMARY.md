# Agent Fitz — Week 3 Quick Summary

**Snapshot:** September 16, 2026  
**Board:** 57 games | 16 qualified | 41 PASS

## Best reusable core

1. **BYU -17.5 (frozen)** — score 82, STRONG
2. **Houston +7.5** — score 81, STRONG
3. **Clemson -3.5** — score 79, GOOD

## Paper tickets

### 3-leg

- BYU -17.5 (frozen)
- Houston +7.5
- Clemson -3.5

### 5-leg

- Same three picks above
- Georgia -24.5
- Miami -20.5

### 8-leg

- Same five picks above
- Arizona State -5.5
- Connecticut -3
- James Madison +2.5

## Next qualified plays

| Score | Pick | Matchup | Kickoff (ET) |
|---:|---|---|---|
| 75 | Notre Dame -29.5 | Michigan State at Notre Dame | Sat 7:30 PM |
| 75 | Texas -30 (frozen) | UTSA at Texas | Sat 8:00 PM |
| 74 | Old Dominion -2.5 (frozen) | East Carolina at Old Dominion | Sat 6:00 PM |
| 74 | Virginia -9.5 (frozen) | West Virginia at Virginia | Sat 7:30 PM |
| 73 | North Texas +3 | North Texas at Texas State | Sat 12:00 PM |
| 72 | Fresno State -6.5 | Fresno State at San Jose State | Sat 11:00 PM |
| 71 | Arizona -34.5 | Northern Illinois at Arizona | Sat 10:30 PM |
| 70 | Colorado +3.5 | Colorado at Northwestern | Sat 7:30 PM |

## Important line note

Use the frozen ticket line for grading. The live full-board snapshot moved to
BYU -18, Old Dominion -3, Virginia -10.5, and Texas -30.5. The historical ticket
lines were intentionally preserved.

## Easy Termux commands

```bash
cd ~/agent-fitz
python agent_fitz_cfb.py summary --file agent_fitz_week3_full_board_2026.json
```

Tickets only:

```bash
python agent_fitz_cfb.py cards --season 2026 --week 3
```

This is paper analysis only. Recheck lines, injuries, quarterbacks, and game
status before kickoff.
