# Agent log (newest on top)

## 2026-11-27  CTO/DEV
- Did: test cycle on main green at the start (459 passed, simulated run and
  check_docs OK). Took the top Product ask, collateral check slice (b): split
  shipments. `check_split` runs the four checks over several bills of lading
  together (each names the order, together exactly its TEU and tonnes, one vessel,
  each held by the plant and unpledged, the whole set tied to one swap, all or
  none). Demo: `--collateral split` binds; `split-pledged` and `split-short`
  refuse with the reason. 81 new tests; 540 pass, 0 fail. Simulated run unchanged;
  $68,000 unchanged. Mock documents, a proposed check.
  https://github.com/UdiRuni/stead-ai/commit/f672dec546d00216692c9dcf97f1a591dcbbf873
- Found: nothing from outside sources today (no web research needed for this slice).
- For CEO: nothing required. Assumption to keep in mind if wording mentions split
  shipments: parts on different vessels are refused, not handled. Collateral item
  (c) (which real document and register a check would read) needs counsel or a
  trade finance reader, so it is parked; next CTO run moves to backtest step 2
  berth areas or the purchase route sources.
- Needs Udi: nothing new. AIS data request from 2026-11-21 still stands.

## 2026-11-26  CEO/Product
- Did: acted on the CTO's 2026-11-26 note: https://github.com/UdiRuni/stead-ai/pull/9
  adds one spoken line and a pause point for the new collateral check block to
  `docs/application/video_script.md` (now about 700 words, about 4 min 40 s). Deck and
  brief untouched. Checks at start: check_docs OK, 459 tests pass. Lloyd's Lab list
  done; next outside-reader test 28 Nov.
- Found: accelerator page re-read, Cohort 18 dates unchanged, no themes, no attendance
  terms (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
  No Sea-Intelligence October 2026 release found; 50.6% and 6.65 days stand. No new
  move found for Otonomi, FourKites, Kpler or Windward; project44 news surfaced is
  Nov 2025 and Apr 2026 (LunaPath.ai, AI agents), no insurance or stock lending
  (https://www.freightwaves.com/news/project44-acquires-lunapath-ai-to-accelerate-ai-agent-orchestration-across-global-supply-chains).
- For CTO: nothing new.
- Needs Udi: review PR 9. Unchanged: a named cargo or TDI advisor and first
  underwriter or plant interviews before 9 Dec.

## 2026-11-26  CTO/DEV
- Did: test cycle on main green at the start (414 passed, simulated run and
  check_docs OK). Took the top Product ask, collateral check slice (a): the demo now
  runs the four checks at T-8, before bind, shown as step 3 on screen and as a term
  sheet section after "Goods". `--collateral pledged` (or mismatch, bank-holds,
  second-swap) shows the "no swap" path with every reason, and says the purchase
  route needs no such security; `released` binds. 45 new tests; 459 pass, 0 fail.
  Simulated run unchanged; $68,000 unchanged. Mock documents, a proposed check.
  https://github.com/UdiRuni/stead-ai/commit/64569adcc78a9fe025c58694a1c448e208e8bbfe
- Found: nothing from outside sources today (no web research needed for this slice).
- For CEO: the demo screen changed. `docs/application/video_script.md` section 4
  describes alert, match, term sheet; there is now a "3. COLLATERAL CHECK ... (MOCK
  DOCUMENTS, a proposed check)" block before RESULT, and the term sheet is "4.". The
  script's pause points still exist. Optional: one line in the script ("before the
  loan binds, it checks the late boxes are the plant's and not pledged elsewhere")
  and a 10 second `--collateral pledged` run. Keep "propose": no register or bank is
  connected and the rules are assumptions.
- Needs Udi: nothing new. AIS data request from 2026-11-21 still stands.

## 2026-11-25  CEO/Product
- Did: no docs/ change; nothing material today. Checks at start: check_docs OK, 414
  tests pass. No open CEO pull request (PR 8 merged 2026-11-24). Lloyd's Lab list done;
  next outside-reader test 28 Nov. Noted the CTO's collateral check mock; materials
  already say "propose", so no wording change.
- Found: searches still show September 2026 as the latest Sea-Intelligence release
  (https://globalmaritimehub.com/global-schedule-reliability-edges-higher-in-september-2026/);
  50.6% and 6.65 days stand. Lab cohorts page has no Cohort 18 content
  (https://www.lloyds.com/insights/lloyds-lab/lloyds-lab-accelerator/cohorts).
  Accelerator, FAQ and Sea-Intelligence pages could not be opened today (permission
  error); dates and criteria carried over. No new move found for Otonomi, project44,
  FourKites, Kpler or Windward; the project44 release that surfaced is from Nov 2025
  and mentions no insurance or stock lending.
- For CTO: nothing new.
- Needs Udi: unchanged: a named cargo or TDI advisor and first underwriter or plant
  interviews before 9 Dec.

## 2026-11-25  CTO/DEV
- Did: test cycle on main green at the start (352 passed, simulated run and
  check_docs OK). Took the top Product ask, collateral check before a loan, slice 1:
  `(cd poc && python3 -m steadpoc.collateral)` runs four checks before a loan binds
  (document matches the order; plant holds the original document; no security
  interest in force on the bind day; one lot backs one live swap) and lists every
  failing reason at once. Five mock cases: clean lot binds; same lot for a second
  swap, wrong grade and tonnes, and bank holding the originals under a letter of
  credit are refused; a pledge released before the bind day binds. 62 new tests;
  414 pass, 0 fail. Simulated run unchanged. Mock data, a proposed check.
  https://github.com/UdiRuni/stead-ai/commit/97aa617645b574ec49e7c5ef4a17263f24272ce4
- Found: nothing from outside sources today (no web research needed for this slice).
- For CEO: the brief and slide 5 line in PR 8 ("we propose to check...") now has a
  working mock behind it. Keep it "propose": the rules (exact tonnes, who counts as
  holder) are assumptions, no real register or bank is connected, and a shipment
  split over several bills of lading is not handled yet. Next CTO slice puts the
  check on the demo term sheet, which the video could show.
- Needs Udi: nothing new. AIS data request from 2026-11-21 still stands.

## 2026-11-24  CEO/Product (second pass, Udi in chat)
- Did: on Udi's request, took the collateral lesson from the Vesttoo collapse (forged
  collateral) into the offering: https://github.com/UdiRuni/stead-ai/pull/8 adds a
  proposed check before each loan (late boxes' title clear, not pledged elsewhere, one
  lot per swap) to brief p2 and slide 5 footnote and notes. Vesttoo is not named in
  materials. New Product ask in poc/BACKLOG.md for a demo of the check.
- Found: Vesttoo's collapse came from fraudulent letters of credit
  (https://insurancejournal.com/news/international/2023/08/15/735355.htm).
- For CTO: new Product ask "collateral check before a loan", mock data only.
- Needs Udi: review PR 8.

## 2026-11-24  CEO/Product
- Did: no docs/ change; nothing material today. Checks at start: check_docs OK, 352
  tests pass. No open CEO pull request. Lloyd's Lab list done; next outside-reader test
  28 Nov.
- Found: latest Sea-Intelligence release is still September 2026 (press room item 415,
  https://www.sea-intelligence.com/press-room/415-global-schedule-reliability-records-a-marginal-gain-in-september);
  no October release found, so 50.6% and 6.65 days stand. Lab cohorts page shows nothing
  on Cohort 18 yet (https://www.lloyds.com/insights/lloyds-lab/lloyds-lab-accelerator/cohorts).
  Accelerator and FAQ pages could not be opened today (permission error); dates and
  criteria carried over. No new move found for Otonomi, project44, FourKites, Kpler or
  Windward in searches.
- For CTO: nothing new. Noted your partial LA/Long Beach port file; materials do not
  claim a real AIS run.
- Needs Udi: unchanged: a named cargo or TDI advisor and first underwriter or plant
  interviews before 9 Dec.

## 2026-11-24  CTO/DEV
- Did: test cycle on main green at the start (305 passed, simulated run and
  check_docs OK). AIS and other data hosts still refused by the sandbox proxy
  (HTTP 403), so real AIS files stay blocked. Took backtest step 2 slice (a): polygon
  port areas and a parser for positions as printed in a regulation, plus the first
  real port file, `poc/data/ports/los_angeles_long_beach.json`: the six commercial
  anchorages of 33 CFR 110.214 (B, C, D, E inside; F, G outside the breakwaters).
  No berth areas yet, so the file is marked partial: `--check-port` describes it, a
  run refuses it. 47 new tests; 352 pass, 0 fail. Simulated run unchanged.
  https://github.com/UdiRuni/stead-ai/commit/153fd43191bdd86d74890c77a99add0a3f2130a2
- Found: anchorages F and G were redrawn by a final rule of 9 Sept 2025, effective
  9 Oct 2025 (https://www.govinfo.gov/content/pkg/FR-2025-09-09/pdf/2025-17318.pdf);
  B to E from FindLaw's copy of 110.214, current as of 2 Jan 2025
  (https://codes.findlaw.com/cfr/title-33-navigation-and-navigable-waters/cfr-sect-33-110-214/).
  Datum NAD 83. eCFR was not reachable; vertices must be checked against it before a
  real run. Read through a text tool 2026-11-24.
- For CEO: nothing to change in docs/. If the application says the backtest will use
  real vessel arrivals, it is still true that no real AIS file has been run; the port
  definition is now partly in place (anchorages, not berths).
- Needs Udi: nothing new. The AIS data request from 2026-11-21 still stands (one
  Marine Cadastre daily file for Los Angeles/Long Beach, put in the repo, would unblock
  the first real run once berths are drawn).

## 2026-11-23  CEO/Product
- Did: Monday re-score on main (scorecard): Team 2, Product 3, Programme 3, all
  unchanged; noted PRs 1 to 7 are merged so "waits for Udi" rows are live. No docs/
  change: nothing material today. Lloyd's Lab list done; next outside-reader test 28 Nov.
  Checks at start: check_docs OK, 305 tests pass. No open CEO pull request.
- Found: accelerator page re-read, Cohort 18 dates unchanged, no themes, no attendance
  terms (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
  FAQ page could not be opened today; criteria carried over. No Sea-Intelligence October
  2026 release found yet; September figures stand. No new move found for Otonomi,
  project44, FourKites, Kpler or Windward.
- For CTO: nothing new. Video script may later use `steadpoc.demo --no-cash`, per your note.
- Needs Udi: biggest gap unchanged: a named cargo or TDI advisor and first underwriter or
  plant interviews before 9 Dec.

## 2026-11-23  CTO/DEV
- Did: test cycle on main green at the start (273 passed, simulated run and
  check_docs OK). AIS hosts still refused by the sandbox proxy today
  (marinecadastre.gov, coast.noaa.gov: HTTP 403), so backtest step 2 and long stop
  part (1) stay blocked. Took purchase route slice (a): the demo term sheet now has a
  section "Or the plant buys the stock outright (assumptions)" with cost to the
  plant, which route is cheaper and why, when the loan wins, and what stead.ai earns
  on each. Blocked purchase (no cash, no room) says the loan is the route. New flags
  `--hold-days`, `--price-change`, `--storage`, `--no-cash`, `--no-room`. 32 new
  tests; 305 pass, 0 fail. Simulated run unchanged.
  https://github.com/UdiRuni/stead-ai/commit/a277dd84f0fb1497008260076c4e2148e8137532
- Found: nothing new from outside sources. On the default (assumed) inputs the demo
  says buying is cheaper ($31,890 against $68,000), as purchase.py did on 2026-11-22.
- For CEO: the demo now answers outside-reader question 1 on screen. If the video
  shows the term sheet, it will show buying as cheaper on our assumptions; the script
  should say the loan is for plants short of cash or room, or avoiding price risk
  (`python3 -m steadpoc.demo --no-cash` shows that path). No published number
  changed; test_worked_case.py untouched.
- Needs Udi: nothing new. The AIS data request from 2026-11-21 still stands.

## 2026-11-22  CEO/Product (design refresh, Udi in chat)
- Did: on Udi's request, restyled deck and brief to the Concordant deck's look:
  https://github.com/UdiRuni/stead-ai/pull/7 (navy, teal, coral, amber, purple; Cambria
  and Calibri; shadow cards; section pills; fade transitions and card entrance
  animations). Words, numbers and notes unchanged, verified. The restyle script is not
  in the repo; future edits keep the new design (house rule 9).
- Needs Udi: review PR 7, ideally opening the .pptx in PowerPoint to see the motion.

## 2026-11-22  CEO/Product (PR 6 merged)
- Did: checked the merge of https://github.com/UdiRuni/stead-ai/pull/6: its last commit
  e1cfae2 is on main and docs/ on main match it exactly. Nothing left unmerged.
- Needs Udi: nothing.

## 2026-11-22  CEO/Product (fourth pass, Udi in chat)
- Did: found that PR 5 was merged after its first commit only; commits 3efdfd5 (Udi
  full time, POC on mock data, why we join) and 0be7c5b (mission, vision, offering)
  never reached main. Cherry-picked both, unchanged, into
  https://github.com/UdiRuni/stead-ai/pull/6, plus Ronit full time and attendance
  (London for mandatory weeks and main events). Charter settled facts and scorecard
  updated.
- Found: Cohort 16 handbook allowed flexible working with three mandatory London weeks
  (https://www.enterprise-ireland.com/documents/lloyd-s-lab-accelerator-cohort-16-information-handbook-pdf-en-172386.pdf);
  the Lab FAQ says nothing on attendance (https://www.lloyds.com/insights/lloyds-lab/faqs).
- Needs Udi: review PR 6. When merging, check the PR is not still receiving commits.

## 2026-11-22  CEO/Product (third pass, Udi in chat)
- Did: mission, vision and per-user offering from Udi's framework deck added to
  https://github.com/UdiRuni/stead-ai/pull/5 (slide 8 kicker and cards, brief lead,
  answers, video hook, product_framework.md). Udi said yes to keeping his facts settled:
  new "Settled facts from Udi" section in agents/CEO_PRODUCT.md (full time, POC on mock
  data, co-design as the reason to join, interviews through Lab connections, mission,
  vision, north star).
- Needs Udi: review PR 5; Ronit's commitment.

## 2026-11-22  CEO/Product (second pass, Udi in chat)
- Did: on Udi's instructions, added to https://github.com/UdiRuni/stead-ai/pull/5
  (commit 3efdfd5): Udi full time (slide 9, brief, answers, video); "working proof of
  concept, on mock data"; "why we join the Lab" as co-design plus interviews with
  underwriters, brokers and insured plants met through mentors (slide 10, brief, notes,
  answers, video). Interviews framed as research, never as a request for customers.
  Video script now about 660 words. Scorecard commitment and interview rows updated.
- Needs Udi: Ronit's time commitment and whether you both can attend the London weeks.

## 2026-11-22  CEO/Product
- Did: outside-reader questions 1 and 2 fixed in words, added to
  https://github.com/UdiRuni/stead-ai/pull/5 (commit 59f7320, branch merged up to main
  first): slides 5 and 6 and notes now say the 11-day case sits inside the TDI deductible,
  so the plant pays and the syndicate's saving applies only past the deductible; the
  $8,000 a month carry is labelled an assumed 8% a year (slide 7 footnote, brief table);
  slide 7 notes say when the loan beats buying, per the CTO. answers.md and video script
  matched. No worked-case number changed. Checks at start: check_docs OK, 273 tests pass.
  PR 5 had no comments. Scorecard notes updated.
- Found: Lab accelerator page re-read, Cohort 18 dates unchanged, no themes
  (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
  Sea-Intelligence September 2026 figures (50.6%, 6.65 days) re-confirmed, published
  29 Oct; no October release found
  (https://www.freshplaza.com/asia/article/9887399/global-shipping-schedule-reliability-improves-to-50-6-in-september/).
  No new competitor move in searches (Otonomi, project44, FourKites, Kpler, Windward).
- Not done: the Aon TDI page could not be opened today; no deductible figure was
  changed, slides only align with the brief's existing sourced line.
- Next CEO run (Monday 23 Nov): weekly re-score and FAQ re-read.
- For CTO: nothing new. Keep `purchase.py` labelled as assumptions.
- Needs Udi: review PR 5 (now also the slide 5 and 6 wording and the 8% label).
- Update 2026-11-22: pull request 5 was merged by Udi at 06:36 UTC with no comment, so
  the video script, answers draft and slide 5 to 7 wording are live on main. No open CEO
  pull request.

## 2026-11-22  CTO/DEV
- Did: test cycle on main green at the start (236 passed, simulated run and
  check_docs OK). Long stop part (1) and backtest step 2 are still blocked on AIS
  data, so I took the next Product ask: purchase route against loan route,
  `steadpoc/purchase.py`, `(cd poc && python3 -m steadpoc.purchase)`. Cost to the
  plant of buying outright (capital and storage on the extra lot, spot premium, price
  move while held, fee) against the published $68,000 loan, what stead.ai earns on
  each, break-evens, cash and room blockers, sensitivity table. 37 new tests; 273
  pass, 0 fail. Simulated run unchanged.
  https://github.com/UdiRuni/stead-ai/commit/11d6f368a977539baac222990d304efeaa7768ae
- Found (assumptions, not data): the brief's "about $8,000 a month" equals 8% a year
  cost of capital on $1.2M; I found no source for it in the repo. On that figure,
  buying is cheaper for the plant in the worked case: about $32,000 through us (2%
  fee, assumed, same as the loan fee) or about $8,000 direct, against $68,000. The
  loan wins only if the plant has no cash or no room, or the price of the extra lot
  falls more than about 3% (5% direct) while it is held, or it is held over about
  167 days, or outside storage costs over about $30 per TEU per day. stead.ai earns
  $24,000 on either route at a 2% fee.
- For CEO: answer to outside-reader question 1, honestly: the loan is the route for
  plants short of cash or room, or that do not want price risk on double stock (the
  brief already cites the 2026 polypropylene swing); otherwise buying is cheaper and
  we earn the same fee. Do not claim the loan is cheaper in general. The $8,000 a
  month figure needs a source or an "assumed 8% cost of capital" label in deck and
  brief. No published number changed; test_worked_case.py untouched.
- Needs Udi: nothing new. The AIS data request from 2026-11-21 still stands.

## 2026-11-21  CEO/Product
- Did: outside-reader test (Lloyd's Lab item 6, the last item). Three hardest
  reviewer questions, with where we answer them and the gap, added to the scorecard on
  main ("Outside-reader test, 2026-11-21"). Moved "Purchase route" up to Product asks in
  `poc/BACKLOG.md`. No change to docs/. Checks at start: check_docs OK, 236 tests pass.
  PR 5 has no comments.
- Found: (1) our own table prices buy spot at about $8,000 a month, so a reviewer will
  ask why borrow for $68,000; (2) the brief says the 11-day case sits inside the TDI
  deductible, but slide 5 Pillar A and slide 6 credit the syndicate with avoiding a
  claim in that case; (3) the deck shows the $16,000 placeholder with no range or
  accumulation limit. Lab page re-read: Cohort 18 dates unchanged, no themes, about 10
  teams from 150 to 200 applications
  (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator);
  FAQ criteria and video/deck guidance unchanged (https://www.lloyds.com/insights/lloyds-lab/faqs).
  No Sea-Intelligence October 2026 release found in search; September figures stand.
  No new competitor move found (searches on Otonomi, project44, FourKites, Kpler,
  Windward).
- Not done: Sea-Intelligence press room could not be opened (fetch refused).
- Next CEO run: propose the slide 5 Pillar A and slide 6 wording fix (question 2) in
  pull request 5, words only, no number changes. Weekly re-score on Monday 23 Nov.
- For CTO: Product ask "purchase route against loan route" is new at the top of the
  backlog; it answers outside-reader question 1.
- Needs Udi: review PR 5. Say whether the deck should keep leading Pillar A with the
  thin-stock $68k figure, or whether you prefer a different TDI example.

## 2026-11-21  CTO/DEV
- Did: test cycle on main was green at the start (186 passed, simulated run and
  check_docs OK). Long stop part (1) still waits for backtest step 2, so I started
  that: slice 1, `steadpoc/portcalls.py`. It turns Marine Cadastre AIS CSV/ZIP files
  into port calls (arrival, first moored, waiting time, calls cut off by the data
  window flagged and left out) and lateness against each vessel's own earlier calling
  interval, earlier calls only. Every threshold is an assumption in `Rules`. 50 new
  tests, all on invented reports. Now 236 pass, 0 fail.
  https://github.com/UdiRuni/stead-ai/commit/cd9a40aeaf6a5f11559153a5f1555e11c8ec7d1f
- Found: the AIS download hosts (coast.noaa.gov, marinecadastre.gov, the Azure blob
  store) are refused by the sandbox proxy, so no real file was run; CC0 licence
  confirmed on https://github.com/ocm-marinecadastre/ais-vessel-traffic. Details in
  `poc/DATA_AUDIT.md`, "Step 2 progress". Simulated run unchanged.
- For CEO: nothing in deck, brief or PR 5 changes. Do not say we have measured real
  arrivals yet: the extractor exists, real data has not been run through it.
- Needs Udi: to run real data, either allow the agent sandbox to reach
  coast.noaa.gov and ocmgeodatastor1.blob.core.windows.net, or download one month of
  daily files for one US container port and put them (or a cut of them) in the repo.

## 2026-11-20  CEO/Product
- Did: draft application answers (Lloyd's Lab item 5), added to
  https://github.com/UdiRuni/stead-ai/pull/5 (commit e44ccba, branch
  `ceo/2026-11-19-video-script`): `docs/application/answers.md`, 17 likely questions
  tagged to team, product or programme, with `[Udi: ...]` blanks. Scorecard updated on
  main. Checks at start: check_docs OK, 186 tests pass. PR 5 had no comments.
- Found: the Cohort 17 form questions are not public; the Lab FAQ, Sonr's Cohort 17
  page and the Cohort 16 handbook give criteria, themes and dates only
  (https://www.lloyds.com/lloyds-lab/faqs, https://sonr.global/lloyds-lab/,
  https://www.enterprise-ireland.com/documents/lloyd-s-lab-accelerator-cohort-16-information-handbook-pdf-en-172386.pdf).
  Cohort 18 dates unchanged, no themes; about 10 teams from 150 to 200 applications
  (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
  Cohort 16 handbook: "Insurance experience not required." No new competitor move found
  in searches. Nothing material for deck or brief.
- Not done: Sea-Intelligence, Marsh, ICC, Otonomi alumni and WTW pages could not be
  opened today (fetch refused), so no figure was re-verified; answers reuse merged
  figures and flag them for re-check before submission.
- Next CEO run: item 6, outside-reader test. On 9 Dec map answers to the real form.
- For CTO: answers.md cites the stock feed as "a proposed format and a sample feed
  (invented data)", per your note. Keep that true.
- Needs Udi: review PR 5; fill the `[Udi: ...]` blanks (company details, commitment,
  interviews held, any agreed advisors).

## 2026-11-20  CTO/DEV
- Did: test cycle on main was green at the start (131 passed, simulated run and
  check_docs OK). Long stop step 2 part (1) waits for backtest step 2, so I took the
  next Product ask: stock feed format and a sample feed. `poc/STOCK_FEED.md` (proposed
  nine-column CSV), `steadpoc/stockfeed.py` (lists every error and warning by line in
  one pass; any error means no lots), `poc/data/sample_stock_feed.csv` (ILLUSTRATIVE,
  the demo's invented lots), `python3 -m steadpoc.stockfeed FILE` and
  `python3 -m steadpoc.demo --stock-feed FILE`. Now 186 pass, 0 fail.
  https://github.com/UdiRuni/stead-ai/commit/dd16a2f86239c8c15a5e3032487d9bfeeedc358b
- Found: decisions recorded in STOCK_FEED.md: values compared exactly (QA approves
  exact codes, no case folding); one snapshot date per feed; days counted from the
  match day; a snapshot over 1 day old is a warning (assumption). Open questions for
  distributors: tonnes or bags rather than TEU, customs status, promised lots.
  Simulated run unchanged.
- For CEO: the Lab plan's weeks 7 to 8 line ("define the stock feed ... on a sample
  feed") now has something to show: the format is a proposal, the sample is invented,
  no distributor sends a feed. Say it that way. Default demo output is unchanged, so
  the video script still matches.
- Needs Udi: nothing.

## 2026-11-19  CEO/Product
- Did: video script (Lloyd's Lab item 4), proposed in
  https://github.com/UdiRuni/stead-ai/pull/5 (branch `ceo/2026-11-19-video-script`):
  `docs/application/video_script.md`, about 630 spoken words (about 4 min 10 s), shot
  list on deck slides 2 to 6, 9 and 10 and a screen demo of `python3 -m steadpoc.demo`
  with pause points, plus a table of every fact said aloud with its source. Scorecard
  application package rows updated on main. Checks at start and end: check_docs OK,
  131 tests pass. No open PR at start (pull request 4 merged).
- Found: Cohort 18 dates unchanged, themes still not published
  (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
  No Sea-Intelligence October 2026 release found yet; September (50.6%, 6.65 days)
  stands (https://www.freshplaza.com/asia/article/9887399/global-shipping-schedule-reliability-improves-to-50-6-in-september/).
  No new competitor move or entrant that finds or lends stock. Nothing material for
  deck or brief.
- Not done: could not re-open the TDI deductible sources (Miller, Aon page empty) or
  Marsh's delay cover page today, so the script leaves those numbers out. The brief and
  deck still carry them, sourced earlier; re-check when the pages open.
- Next CEO run: application answers (item 5), `docs/application/answers.md`, from the
  Cohort 17 questions if they can be found; add to pull request 5 if still open.
- For CTO: the script narrates the demo as it runs today (ALERT line, "chosen" lot,
  term sheet). If you change demo wording, note it in the log so the script follows.
- Needs Udi: approve or comment on pull request 5; say whether Ronit records a line.

## 2026-11-19  CTO/DEV
- Did: test cycle on main was green at the start (112 passed, simulated run and
  check_docs OK, deck 10 slides). Built long stop step 2, part (3): the demo term sheet
  now shows the long-stop date (T+30, assumption), the pricing method's estimate beside
  the $16,000 placeholder (labelled "Assumptions, not a quote; not in the total"), and
  the per-vessel limit check. Two new "no swap" paths, each with a plain reason: boxes
  due on or after the long stop, and the vessel limit full. Flags `--long-stop N` and
  `--vessel-exposure USD`. Now 131 pass, 0 fail.
  https://github.com/UdiRuni/stead-ai/commit/5271bedd4da1548d0bf37a4ec6a7c079e707624f
- Found (ILLUSTRATIVE, assumptions): base case method estimate $17,230 (5.7% chance of
  passing T+30); at T+21 it is $66,688. The worked case total stays $68,000. Simulated
  run unchanged.
- For CEO: if the video shows the demo term sheet, it now has a "Method estimate" row.
  Narrate it as "how the premium would be built, on assumptions", never as a price. The
  "Built so far" wording (alert to term sheet, illustrative data) is still true. No
  published number changed.
- Needs Udi: nothing.

## 2026-11-18  CEO/Product
- Did: team evidence (Lloyd's Lab item 3), proposed in
  https://github.com/UdiRuni/stead-ai/pull/4 (branch `ceo/2026-11-18-team-evidence`):
  a "Built so far" line on deck slide 9 and its notes, and in the brief's team
  paragraph (proof of concept, alert to term sheet, illustrative data; backtest on 23
  months of public data). Three words cut from the brief's eBL bullet to stay at 2
  pages. Checks at start and end: check_docs OK, 112 tests pass. No open PR at start.
  Scorecard team row 2 updated on main.
- Found: no Sea-Intelligence release for October 2026 yet; latest is still September
  (50.6%, 6.65 days), so our figures stand
  (https://www.sea-intelligence.com/press-room). Cohort 18 dates unchanged, no themes
  yet (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
  FourKites Inventory Twin update (11 May 2026) still moves surplus between the
  customer's own sites; no outside stock, loan or cover
  (https://itbrief.com.au/story/fourkites-adds-live-logistics-links-to-inventory-twin).
  No new entrant that finds or lends stock found. Nothing material.
- Not done: Marsh page and Logistics Viewpoints article still could not be opened
  (permission prompt; redirect loop). Nothing changed on trust.
- Next CEO run: video script (item 4), `docs/application/video_script.md`, using the
  CTO's suggested shot list; add it to pull request 4 if still open.
- For CTO: nothing new. Demo is now cited in pull request 4; keep its wording
  ("illustrative data") true if the demo changes.
- Needs Udi: approve or comment on pull request 4. One point to judge: the code was
  written by our AI agents; say if "AI-assisted" should be added to "Built so far".
- Update 2026-11-18: pull request 4 was merged by Udi with no comment, so the "Built so
  far" line is live on main. No open CEO pull request.
- Udi answered 2026-11-18: leave "Built so far" as merged, no "AI-assisted". Do not ask
  again. If a reviewer asks who built the POC, the team directs AI agents and owns the
  design and the economics.

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
