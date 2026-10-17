# Agent Fitz — Week 7 Saturday paper preview

**Games:** Saturday October 17, 2026 (all listed times Eastern)  
**Research update:** October 16, 2026  
**Scope:** 20 Saturday games screened; 8 qualified (score ≥ 70), 12 PASS. The complete Saturday FBS slate was **not** independently researched.  
**Status:** Research-only preview. Market lines are source snapshots, not live sportsbook quotes; re-check before kickoff. No wager placed, no actual Termux execution yet.

## 3-leg paper ticket

| Selection | Game | Score |
|---|---|---:|
| Houston -4.5 | Oklahoma State at Houston (19:30 ET) | 83 |
| Penn State +6.5 | Penn State at Michigan (15:30 ET) | 82 |
| Northwestern -7.5 | Northwestern at Michigan State (12:00 ET) | 81 |

## 5-leg paper ticket

| Selection | Game | Score |
|---|---|---:|
| Houston -4.5 | Oklahoma State at Houston (19:30 ET) | 83 |
| Penn State +6.5 | Penn State at Michigan (15:30 ET) | 82 |
| Northwestern -7.5 | Northwestern at Michigan State (12:00 ET) | 81 |
| Wake Forest -9.5 | Wake Forest at California (22:30 ET) | 79 |
| New Mexico -14.5 | New Mexico at Hawaii (22:30 ET) | 77 |

## 8-leg paper ticket

| Selection | Game | Score |
|---|---|---:|
| Houston -4.5 | Oklahoma State at Houston (19:30 ET) | 83 |
| Penn State +6.5 | Penn State at Michigan (15:30 ET) | 82 |
| Northwestern -7.5 | Northwestern at Michigan State (12:00 ET) | 81 |
| Wake Forest -9.5 | Wake Forest at California (22:30 ET) | 79 |
| New Mexico -14.5 | New Mexico at Hawaii (22:30 ET) | 77 |
| Texas Tech -14.5 | Arizona State at Texas Tech (15:30 ET) | 76 |
| Kentucky +6.5 | Kentucky at Oklahoma (19:30 ET) | 76 |
| Utah -15.5 | Utah at Colorado (22:15 ET) | 75 |

## PASS games

- **Notre Dame at BYU** — PASS: BYU personnel uncertainty versus competing models; difficult to justify double-digit road favorite.
- **Ohio State at Indiana** — PASS: top-five matchup with balanced projections; no supported ATS advantage.
- **Nebraska at Oregon** — PASS: Oregon quarterback status uncertain in pregame reporting; avoid pre-confirmation spread.
- **Florida State at Miami** — PASS: Miami favored by roughly three touchdowns, but variance and roster/weather uncertainty; no verified margin edge.
- **Alabama at Tennessee** — PASS: high-variance ranked rivalry without an independently established spread edge.
- **Florida at Texas** — PASS: guide listed Texas -10.5, but no independently established edge at this number.
- **Mississippi State at LSU** — PASS: significant Mississippi State personnel questions; no reliable model-versus-market advantage identified.
- **Missouri at Ole Miss** — PASS: guide listed Ole Miss -6; closely contested top-15 matchup, no research-qualified ATS edge.
- **North Carolina at Duke** — PASS: guide listed Duke -3.5; no validated spread advantage for either side.
- **Auburn at Georgia** — PASS: guide listed Georgia -20.5; large favorite plus rivalry variance, no validated edge.
- **Wisconsin at UCLA** — PASS: guide listed UCLA -3; no independently established price advantage.
- **TCU at Baylor** — PASS: guide listed Baylor -5.5; no independently validated edge.

## How to run this on Termux

```bash
cd ~/agent-fitz
git pull --ff-only
python agent_fitz.py freeze --board boards/agent_fitz_week7_2026.json --append
python agent_fitz.py cards --season 2026 --week 7
```

**Research limitations:** Subjective 0–100 rankings are not measured probabilities. Scores/qualifications assume the stated lines; a worse available line may invalidate a pick. Strong picks recur in the bigger tickets by design. Grading should occur only after games with verified results. See [board JSON](../boards/agent_fitz_week7_2026.json) for per-matchup notes and sources.
