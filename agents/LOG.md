# Agent log (newest on top)

## 2026-11-15  Setup (Claude, with Udi)
- Did: created the repo layout, both agent charters and the shared rules in `CLAUDE.md`.
- Did: added the short deck (9 slides) and put portraits of Udi and Ronit on the team
  slide. The full deck and the original 2-pager PDF are frozen in `docs/archive/`.
- Did: rebuilt the 2-page brief as `docs/brief/brief.json` plus `build_brief.py`,
  because the original build script was lost. Text and links match the original; the
  layout is a close reproduction, not pixel identical.
- Did: seeded the POC (worked-case economics, alert rule, matching, simulated run)
  with 14 passing tests, and `tools/check_docs.py` for the house rules.
- Found: every published worked-case number follows from the model (6 days stopped,
  $1.08M, $68,000, about 77% annualized, 83% to 94% lower loss, $1.6M per 100 swaps).
- For CTO: start at the top of `poc/BACKLOG.md`.
- For CEO: first run should verify every source link in `brief.json` still resolves.
- Needs Udi: nothing.
