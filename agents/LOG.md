# Agent log (newest on top)

## 2026-11-16  CEO/Product
- Did: plain-language pass on deck and brief (Lloyd's Lab item 1) and schedule figures
  moved from July to September 2026, proposed in
  https://github.com/UdiRuni/stead-ai/pull/1 (branch `ceo/2026-11-16-plain-language`).
  Monday re-score in the scorecard: team 2, product 3, programme 3, all unchanged.
- Found: September 2026 was 50.6% on time and 6.65 days average lateness, Sea-Intelligence
  issue 182 (https://www.freshplaza.com/asia/article/9887399/global-shipping-schedule-reliability-improves-to-50-6-in-september/).
  That page gives the month-on-month moves as +0.9 points and -0.30 days, which does not
  match our August row (49.9%, 6.81 days). August may have been revised.
- Found: Cohort 18 dates confirmed, themes not yet published; Cohort 17 "new products"
  theme asks for "solutions which address supply chain disruption"
  (https://www.lloyds.com/insights/lloyds-lab/cohort-17). The accelerator page offers
  mentors and syndicate pilots and does not mention data.
- Found: Marsh terms unchanged ($1,000 to $250,000; 6, 8 or 10 day marine triggers,
  https://www.marsh.com/en/industries/cargo/expertise/parametric-coverage-for-cargo-delay.html).
  Otonomi launched TRACinSURED with Tag-N-Trac and Solent Freight on 9 Oct 2026: air and
  courier, cash payout (https://www.reinsurancene.ws/otonomi-tag-n-trac-solent-freight-services-launch-parametric-cargo-coverage/).
  Willog, cargo monitoring data for parametric cover, is in Cohort 17
  (https://www.lloyds.com/insights/media-centre/press-releases/lloyds-lab-unveils-cohort-17-following-pitch-day-in-london).
  No entrant found that finds or lends stock. The FourKites stockout article of May 2026
  could not be opened and is the closest neighbour; read it before leaning on "we found
  no one else who".
- Found: accelerators. Techstars London closes 18 Nov 2026
  (https://www.techstars.com/accelerators/london). Insurtech Gateway takes pitches on a
  rolling basis, up to 250k GBP pre-seed (https://www.insurtechgateway.com/incubator/).
  Entrepreneur First, Antler UK and Plug and Play Insurtech publish no deadline.
- Not done: the check of all 32 source links in `brief.json`. The fetch tool wanted a
  permission for each URL that nobody was present to give; only pages reached through
  a search could be opened. Nothing was changed on trust. The Cohort 17 application
  questions were not found online. Next CEO run: programme risk wording (item 2), added
  to pull request 1 if it is still open.
- For CTO: (1) if Udi merges pull request 1, change the two borrowed figures in
  `simulate.py` to 50.6% and 6.65 days. (2) Check the August row in
  `poc/data/schedule_reliability_monthly.csv` against the September release (see above).
  (3) The demo command (first Product ask) is now the item that blocks team evidence
  and the video script.
- Needs Udi: (1) approve or comment on pull request 1. (2) Team is the biggest gap: one
  cargo or TDI underwriting advisor, one polymer distribution advisor, what we may say
  about commitment, and interviews before 9 Dec. (3) Techstars London closes 18 Nov if
  you want it. (4) Allow web fetches without a prompt in this scheduled task, so the
  agents can open source links.
- Udi answered 2026-11-16: (1) pull request 1 approved and merged by Udi on
  2026-11-16, so the CTO note on `simulate.py` (50.6%, 6.65 days) is now live. (2) Team facts: to be decided, do not ask
  again until he reports. (3) Techstars London: not needed, drop it. (4) Web fetches:
  he will allow them in the task settings.

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
