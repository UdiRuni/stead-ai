# Agent log (newest on top)

## 2026-11-18  CTO/DEV
- Did: test cycle on main was green at the start (76 passed, simulated run and
  check_docs OK). Built long stop step 2, part (2), accumulation:
  `(cd poc && python3 -m steadpoc.accumulation)`. Per-vessel and per-event limits on
  agreed value, each refusal with a plain reason; swaps on one vessel must share an
  arrival; expected loss reuses `longstop.py`; Monte Carlo with one slip per vessel
  against independent swaps; a deterministic event stress. Now 112 pass, 0 fail.
  https://github.com/UdiRuni/stead-ai/commit/6821c10d3da574efd0d0e0664b8a44de64e97272
- Found (SIMULATED book of 9 invented swaps, assumed limits $3M per vessel and $7.5M
  per event, 15% severity; not a result, do not quote): expected loss is the same
  either way (about $89,000), but the 99th percentile is about $675,000 with one slip
  per vessel against $465,000 if swaps were independent. A port strike adding 22 days
  costs $1.11M, held under the event limit. The point for underwriters: per-swap
  pricing gets the average right and misses the bad outcome; the limits bound it.
- Found: events are only a stress scenario, not in the Monte Carlo. Putting them in
  needs a sourced event frequency (strikes or closures per year at Rotterdam and
  Antwerp); none looked for today, none invented. Added to the backlog.
- For CEO: if the application or deck answers "how do you control accumulation",
  the supported wording is "the POC caps exposure per vessel and per event and shows
  the loss in a stress scenario; the limits are for underwriters to set". No published
  number changed or looked fragile; the $16,000 placeholder is untouched.
- Needs Udi: nothing.

## 2026-11-17  CEO/Product, second session (Udi present)
- Udi asked: raise the Product score to 5, including product vision enhancements, and
  use his framework deck (clarifying questions, mission, vision, north star, users,
  pain points, solutions, tradeoffs, metrics).
- Did: proposed in https://github.com/UdiRuni/stead-ai/pull/3 (branch
  `ceo/2026-11-17-product-vision`): `docs/application/product_framework.md`, the
  product case on that framework; a new deck slide 8 "Where this goes" (one insured
  swap, then a standing swap line, then delay priced from our records; north star:
  factory stoppage days avoided per insured plant, per year); the brief's long-stop
  row now cites the pricing method. Deck would be 10 slides, the limit.
- Did, on main: `poc/steadpoc/longstop.py`, a first pricing method for the long stop,
  with 7 tests (76 pass). https://github.com/UdiRuni/stead-ai/commit/f1127b7
  Base case about $17,000 against the $16,000 placeholder; $2,000 to over $100,000 as
  the long-stop date and the tail change. Assumptions, not a quote; do not cite the
  numbers. The placeholder and the worked case are unchanged.
- Found: Europe's polypropylene imports were projected above 2 million tonnes for 2025,
  over half from Saudi Arabia and South Korea
  (https://www.chemorbis.com/en/premium-plastics-news/Europe-PP-outlook-for-2026-A-market-in-structural-reset-amid-growing-imports-and-deeper-restructuri/2025/12/05/954179).
  Siemens, True Cost of Downtime 2024: $36,000 an hour in consumer goods, $2.3 million
  an hour at a large car plant
  (https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/TCOD-2024_original.pdf).
  WTW study of 1,000 firms on supply chain cover out of line with concern; it does not
  measure delay
  (https://www.wtwco.com/en-gb/insights/2026/05/mind-the-gap-what-1000-executives-reveal-about-supply-chain-insurance-misalignment).
  Cohort 17 "new products" theme re-read: asks for solutions that "address supply
  chain disruption" (https://www.lloyds.com/insights/lloyds-lab/cohort-17).
- Found: no sourced figure for how many importers hold thin stock, and no full-year
  tonnage for EU polymer imports on the pages that could be opened. Market size is
  arithmetic on assumptions and is kept out of the deck.
- For CTO: the long-stop Product ask is now "step 2" in the backlog: a tail fitted to
  real arrivals, accumulation limits per vessel and per event, and the long-stop date
  and method on the demo term sheet. I built step 1 in your area because Udi asked;
  change it as you see fit. If pull request 3 is merged, the deck has a slide 8 and
  team and plan move to 9 and 10.
- Needs Udi: (1) approve or comment on pull request 3; the swap line is a change of
  vision and is yours to accept or drop. (2) Product cannot reach 5 on writing alone:
  it needs one plant and one underwriter on record, from interviews.

## 2026-11-17  CEO/Product
- Did: programme risk (Lloyd's Lab item 2), proposed in
  https://github.com/UdiRuni/stead-ai/pull/2 (branch `ceo/2026-11-17-programme-risk`).
  Deck slide 9 and notes, footnotes on slides 2 and 3, the brief's plan cards and ask.
  Weeks 1 to 3 run on public data, weeks 7 to 10 on a sample feed and a paper pilot
  unless a distributor has joined, and the ask reads as co-design, not customers.
  Checks at start and end: check_docs OK, 69 tests pass. No open pull request at start
  (pull request 1 was merged).
- Did: scorecard updated on main (scoring guidance, pull request 2 status, two new
  package rows). Two Product asks added to `poc/BACKLOG.md`.
- Found: a "Lloyd's Lab Scoring Guidance" PDF, hosted by Sonr, not by Lloyd's and
  undated: 1 to 5 per criterion; team is quality of work, relevant experience and
  commitment; product is market fit, innovation and market size; programme is product
  development focus, a realistic 10-week plan and traction within the insurance
  industry (https://sonr.global/wp-content/uploads/2023/12/Lloyds-Lab-Scoring-Guidance.pdf).
  We show no market size and no insurance traction today.
- Found: Lab FAQ and accelerator page re-read, unchanged: same three criteria, same
  Cohort 18 dates, no themes yet. The FAQ gives 3 to 8 mentors per team and free
  access to the Insights Hub; no other data
  (https://www.lloyds.com/insights/lloyds-lab/faqs,
  https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
- Found: Sea-Intelligence published a correction on 6 Nov 2026: alliance scores were
  double-counted; "does not impact any carrier or trade scores". Our two figures
  (50.6%, 6.65 days, issue 182) still read the same on its own release page, opened
  today. The correction does not restate the global figure. The release for October is
  not out yet (https://www.sea-intelligence.com/press-room/419-glp-correction,
  https://www.sea-intelligence.com/press-room/415-global-schedule-reliability-records-a-marginal-gain-in-september).
- Found: FourKites Inventory Twin flags a stockout up to 14 days ahead and moves surplus
  between the customer's own sites; no outside stock, loan or cover. "We found no one
  else who" still holds on what we could read
  (https://www.businesswire.com/news/home/20260505928982/en/). The Logistics Viewpoints
  article still could not be opened (redirect loop). Otonomi and FIATA (2 Apr 2026):
  delay cover for forwarders, air, ocean and e-commerce, triggers of 3 to 24 hours;
  payout form not stated; nothing newer found
  (https://www.stattimes.com/amp/air-cargo/fiata-and-otonomi-partner-to-offer-cargo-and-delay-insurance-globally-1358641).
- Not done: Marsh's page could not be re-opened (fetch permission prompt, nobody to
  answer); terms assumed unchanged since 16 Nov, nothing changed on trust. The 32 source
  links in `brief.json` are still not all checked. No new accelerator deadline found.
  Cohort 17 application questions still not found online. Next CEO run: team evidence
  (item 3), citing the POC demo in deck and brief, added to pull request 2 if open.
- For CTO: (1) two Product asks added: a stock feed format with a sample feed, and
  backtest step 2 (real vessel arrivals from open data). Both back lines in pull
  request 2. Keep "price the long stop" first. (2) The demo may keep SABIC PP 575P and
  Geleen, as the brief names the grade. (3) August row: the September release itself
  says +0.9 points and -0.30 days, so August was revised to about 49.7% and 6.95 days;
  your "as first published" note covers it, no change needed.
- Needs Udi: (1) approve or comment on pull request 2. Two points to judge are in its
  description: "real vessel arrivals" means open US data today, and the paper pilot is
  the fallback if no distributor signs a letter of interest. (2) Web fetches worked for
  most pages today; a few sites (Marsh) still prompt.
- Update 2026-11-17: pull request 2 was merged on 2026-11-17, so the programme wording
  is live on main and the two Product asks in `poc/BACKLOG.md` now back published
  lines. No comment was left on the two points to judge. No open CEO pull request.

## 2026-11-17  CTO/DEV
- Did: test cycle on main was green at the start (39 passed, simulated run and
  check_docs OK). Built the top Product ask, the demo command:
  `(cd poc && python3 -m steadpoc.demo --html out/demo.html)`. It walks the worked case
  on screen: three ETA updates, the alert at T-12, the stock match with a plain reason
  for every refused lot, and a one-page term sheet (lender, goods, dates, yield,
  premium, fee, alternatives, what makes the return leg safe). Text and a
  self-contained HTML page. Now 69 tests pass, 0 fail.
  https://github.com/UdiRuni/stead-ai/commit/3f2882e4b355e444473d927464eff32ac91bcc49
- Did: CEO note 1. `simulate.py` now borrows 50.6% on time and 6.65 days (September
  2026), as the brief does since pull request 1 was merged. SIMULATED headline moved:
  per 1,000 shipments, 100 alerts (was 87), 76 warned in time (was 68), 65 swapped
  (was 61). Not a result; do not quote.
- Found: every figure on the term sheet is read from `economics.py`, so the demo shows
  the published worked case exactly ($68,000 as 28 + 16 + 24, about 77% annualized,
  6 days and $1.08M with no action, $390,000 air, 83% to 94% lower). No published
  number looked wrong or fragile.
- Found: CEO note 2, the August row. Not verified: the two Sea-Intelligence pages could
  not be opened today (the fetch permission prompt was not answered in this unattended
  run). By arithmetic only, the September moves quoted by FreshPlaza (+0.9 points,
  -0.30 days) imply August revised to about 49.7% and 6.95 days, against 49.9% and
  6.81 as first published. `poc/data/README.md` already says rows are "as first
  published" and that later releases do not chain, so the file was left unchanged.
- Limits of the demo, stated on screen: ETA updates and distributor stock are invented;
  the premium is marked PLACEHOLDER; the long-stop date reads "Not set"; the delay
  cover row of the brief's comparison is left out because no model reproduces it yet.
- For CEO: (1) the demo is ready for the video script and for citing the POC in deck and
  brief (scorecard, team row 2 and the application package "CTO demo"). Suggested shot
  list: run the command, pause on the ALERT line, on the "chosen" line among the
  refused lots, then on the term sheet. `--delay 4` shows the engine staying silent
  when stock covers the delay, which is worth ten seconds. (2) The demo names SABIC PP
  575P and the Geleen plant, as the brief names the grade. If you would rather show an
  invented grade on video, say so and I will change one line.
- Needs Udi: web fetches are still blocked in the CTO task (permission prompt with no
  one to answer). Please allow them in this task's settings too. Otherwise nothing.

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
