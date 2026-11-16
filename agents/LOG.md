# Agent log (newest on top)

## 2026-11-16  CTO/DEV
- Did: test cycle on main was green (14 passed, simulated run and check_docs OK). Built
  the top Product ask: `poc/DATA_AUDIT.md` and a backtest that runs on public data
  only, `(cd poc && python3 -m steadpoc.backtest)`. Now 39 tests pass, 0 fail.
  https://github.com/UdiRuni/stead-ai/commit/a158b880fc93a0681eb4adfbe1795d1ba50738df
- Did: `poc/data/schedule_reliability_monthly.csv`, 28 months (2024-06 to 2026-09) of
  Sea-Intelligence press-release figures, each row with its link, retrieved today.
- Found: the backtest replays 23 months (5 skipped: Feb to Jun 2025 releases do not
  state the average delay). SIMULATED except the two monthly inputs: about 70 alerts
  per 1,000 shipments on average, 47 in the calmest month (2025-08) to 102 in the
  roughest (2026-08). Not a result; do not quote.
- Found: no source sells 24 months of shipment-level ETA revision history at a
  published price. Tracking APIs follow a container forward from subscription
  (Shipsgo: "the historical data is not available for now", https://shipsgo.com/faq).
  No free archive of past carrier schedules exists that we could find. Free per-vessel
  arrival data covers US, Danish and Norwegian waters only, not Rotterdam or Antwerp.
  Published prices: Sea-Intelligence report from 2,000 EUR a year
  (https://www.sea-intelligence.com/services); VesselFinder port calls 175 EUR per
  5,000 credits (https://www.vesselfinder.com/port-calls-api). Full table and links in
  `poc/DATA_AUDIT.md`.
- Found: latest Sea-Intelligence figures are 49.9% on time and 6.81 days in August 2026
  (https://www.sea-intelligence.com/press-room/410-global-schedule-reliability-continues-to-plummet-in-august)
  and 50.6% and 6.65 days in September 2026
  (https://www.sea-intelligence.com/press-room/415-global-schedule-reliability-records-a-marginal-gain-in-september).
- Note: pages were read through a text-extraction tool. Open a link in a browser before
  reusing any figure or quote in pitch material. The setup step "add_repo" does not
  exist in this environment; the repo was already attached and pushes work.
- For CEO: (1) the plan line "Replay 24 months of tracking and schedule data, plus
  mentors' delay claims" is the fragile one. Evidence in `poc/DATA_AUDIT.md`: schedule
  data for 24 months is public and already replayed; shipment-level tracking history
  is not verified to be for sale; mentor claims data is not needed. Suggested direction
  for a pull request: weeks 1 to 3 run on public schedule data from day one, and the
  Lab's help is an introduction to a shipper or forwarder whose past bookings can be
  replayed. (2) The brief quotes July 2026 (56.4%, 6.06 days). Newer and worse figures
  exist, see above; your call whether to update. If you do, tell me, because
  `simulate.py` borrows the same two numbers. (3) Scorecard, programme row 1: the
  CTO part is done; what remains is the wording in deck and brief.
- Needs Udi: decide whether to ask for quotes for vessel-level history (Xeneta, or
  Sea-Intelligence custom data) and shipment-level history (Vizion, project44,
  Portcast). Agents may not contact vendors. Not needed for the application; it would
  make the week 1 to 3 plan firmer.

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
