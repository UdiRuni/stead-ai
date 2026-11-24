# POC backlog

Top item first. The CTO/DEV agent takes the first open item each day. The CEO/Product
agent may add to "Product asks", which always come before "Engineering".

## Product asks

These come from `agents/LLOYDS_LAB_SCORECARD.md` and close gaps a Lab reviewer
will score.

- [ ] Product: collateral check before a loan (asked by Udi, 2026-11-24; proposed in
      pull request 8). Before a loan binds, the demo checks the late boxes as the
      lender's security: (a) the bill of lading or delivery order matches the grade,
      tonnes and consignee on the order; (b) a register of lots, so one lot backs at
      most one swap; (c) a flag when the plant's bank or another lender already holds
      the shipment as security, and the loan refuses to bind. Mock data only. Why: a
      Lloyd's reviewer will ask how we know the collateral is real and unpledged; the
      deck and brief now say we propose this check, and a demo makes it evidence.

- [ ] Product: long stop, step 2. The first method is in `steadpoc/longstop.py`
      (2026-11-17). Still open: (1) replace the exponential tail with a tail fitted to
      real arrival data (needs backtest step 2, so it waits for that item below);
      (2) done 2026-11-18 and (3) done 2026-11-19, see Done. Why: accumulation is the
      first question a cargo underwriter will ask.

- [ ] Programme: backtest step 2, real vessel arrivals from open data (the first
      Engineering item below, moved up). Slice 1 done 2026-11-21: the AIS port call
      extractor (`steadpoc/portcalls.py`), tested on invented reports. Blocked next:
      the AIS download hosts are not reachable from the agent sandbox (see
      DATA_AUDIT.md, "Step 2 progress"). Next slices: (a) a real port definition with
      its chart source: anchorages done 2026-11-24 (see Done), berth areas still
      open, needs a sourced chart or port map of the container terminals; (b) run real files once a host is reachable or a file is put
      in the repo; (c) feed the call list into the backtest. Why: pull request 2 says weeks 1 to 3 "extend
      our backtest with real vessel arrivals"; a first cut before 17 Jan makes that
      line evidence, not a promise.

- [ ] Product: purchase route, next. Slice 1 done 2026-11-22 (`steadpoc/purchase.py`)
      and (a) done 2026-11-23 (demo term sheet section), see Done. Still open:
      (b) replace the assumed 8% cost of capital and 30 holding days with
      figures a plant or a public source gives; (c) a sourced polypropylene monthly
      price move, so the 3 to 5% break-even can be set against how often it happens.

## Engineering

- [ ] Accumulation, next: put events into the Monte Carlo (chance an event happens and
      the days it adds), and an aggregate limit for the whole book. Needs a sourced
      event frequency first (for example port strikes or closures per year at
      Rotterdam and Antwerp); do not invent one.

- [ ] Backtest step 2 (see `poc/DATA_AUDIT.md` section 4): real per-vessel arrival and
      waiting times at one US port from Marine Cadastre AIS (CC0), with IMF PortWatch
      chokepoint transits as the warning signal. Check the PortWatch licence first.
- [ ] Backtest noise: report each month as the mean of several seeds with a range, so
      single months can be read, not only the trend.
- [ ] Sensitivity table: safety stock days by downtime cost per day, showing where a
      swap beats no action, air freight and delay cover. Output as CSV and as text.
- [ ] Parametric delay cover model that reproduces the published comparison (pays
      $137,500 to $187,500 on the worked case, $250,000 top limit, 6 to 10 day
      triggers). Find the published terms first; if they cannot be reproduced, write
      a "For CEO" note.
- [ ] Long-stop premium: estimate the chance the late boxes pass a long-stop date from
      the delay distribution, price it, and compare with the $16,000 placeholder.
- [ ] Swap timeline as a state machine (alert, match, bind, release, return) with the
      customs limits checked, including the 90 day temporary storage limit.
- [ ] Stock feed, next: the simulation still draws random stock; let it read a feed
      (or several) instead. Open questions for distributors are listed in
      `poc/STOCK_FEED.md` (tonnes or bags, not TEU; customs status; promised lots).
- [ ] Replace the invented delay model with a replay of public schedule reliability
      data. Find sources that may be used and redistributed; record link and date.
- [ ] Command line tool, rest of it: the demo (`python3 -m steadpoc.demo`) walks an
      invented booking. Still open: read a booking, ETA updates and a stock feed from
      files. The stock feed part is done (`--stock-feed`, 2026-11-20); booking and ETA
      updates from files are still open.
- [ ] Demo: add the parametric delay cover row to the term sheet comparison once that
      model exists. (Long-stop date and method estimate added 2026-11-19.)
- [ ] Demo: warn when the long-stop date falls beyond the 90 day temporary storage
      limit, if that matters for the return leg; check the customs rule first.

## Done

- [x] 2026-11-24 Programme: backtest step 2, slice (a) part 1. Polygon port areas and
      positions as printed in a regulation (`Area`, `parse_dms` in `portcalls.py`);
      first real port file `data/ports/los_angeles_long_beach.json` with the six
      commercial anchorages of 33 CFR 110.214 (F and G as amended in 2025). Marked
      partial (no berths): `--check-port` describes it, a run refuses it. 47 new tests,
      including printed sub-anchorage centres falling inside the right polygon.

- [x] 2026-11-23 Product: purchase route on the demo term sheet. New section "Or the
      plant buys the stock outright (assumptions)" between the alternatives and the
      return leg: cost to the plant with each part, loan or purchase cheaper and why,
      when the loan wins (break-evens), what stead.ai earns on each. Blocked routes
      (no cash, no room) say the loan is the route; the swap is still offered. New
      demo flags `--hold-days`, `--price-change`, `--storage`, `--no-cash`,
      `--no-room`. The $68,000 loan rows are unchanged. 32 new tests.

- [x] 2026-11-22 Product: purchase route against loan route, slice 1.
      `(cd poc && python3 -m steadpoc.purchase)`: cost to the plant of buying the
      stock outright (capital and storage on the extra lot, spot premium, price move
      while held, fee) against the published $68,000 loan; what stead.ai earns on
      each; break-even price fall, holding days and storage rate; cash and room
      blockers; sensitivity table. On the brief's own "about $8,000 a month" the
      purchase is cheaper (about $32,000 through us, about $8,000 direct) unless the
      price of the extra lot falls more than about 3% (5% direct) while held, it is
      held over about 167 days, outside storage passes about $30 per TEU per day, or
      the plant lacks cash or room. All inputs assumptions. 37 new tests.

- [x] 2026-11-21 Programme: backtest step 2, slice 1. `steadpoc/portcalls.py` turns
      Marine Cadastre AIS CSV/ZIP files into port calls (arrival, first moored,
      waiting time, cut-off flags) and lateness against each vessel's own calling
      interval, using earlier calls only. `python3 -m steadpoc.portcalls --port
      PORT.json FILES --csv out.csv`. Every threshold is in `Rules`. 50 new tests,
      all on invented reports; no real AIS run yet (hosts blocked).

- [x] 2026-11-20 Programme: stock feed format and a sample feed. `poc/STOCK_FEED.md`
      (proposed CSV schema, nine columns), `steadpoc/stockfeed.py` (parser that lists
      every error and warning with its line number in one pass and returns no lots if
      any error), `poc/data/sample_stock_feed.csv` (ILLUSTRATIVE, the demo's lots),
      `python3 -m steadpoc.stockfeed FILE` to check a feed, and
      `python3 -m steadpoc.demo --stock-feed FILE`. 55 new tests.

- [x] 2026-11-19 Product: long stop, step 2 part (3). The demo term sheet now shows
      the long-stop date (T+30, assumption), the method estimate from `longstop.py`
      beside the $16,000 placeholder (never in the total), and the per-vessel limit
      check from `accumulation.py`. Two new "no swap" paths with plain reasons: boxes
      due on or after the long stop, and vessel limit full. New flags `--long-stop N`
      and `--vessel-exposure USD`. 19 new tests.

- [x] 2026-11-18 Product: long stop, step 2 part (2), accumulation,
      `(cd poc && python3 -m steadpoc.accumulation)`. Per-vessel and per-event limits
      on agreed value with a plain reason for every refusal; boxes on one vessel must
      share an arrival; expected loss from `longstop.py`; Monte Carlo with one slip
      per vessel against independent swaps; deterministic event stress. Simulated
      book, assumed limits. 36 new tests.

- [x] 2026-11-17 Product: first pricing method for the long stop,
      `(cd poc && python3 -m steadpoc.longstop)`. Chance of passing the long stop from
      an exponential tail on the public 6.65 days, net severity share, loss ratio, and
      a sensitivity table. Assumptions, not a quote. The $16,000 placeholder is
      unchanged. 7 new tests. Built by the CEO agent at Udi's request.
- [x] 2026-11-15 Seed: economics of the worked case, alert rule, same-grade matching,
      simulated end-to-end run, 14 tests.
- [x] 2026-11-16 Programme: data audit (`poc/DATA_AUDIT.md`) and a backtest that runs
      on public data only (`python3 -m steadpoc.backtest`, 28 sourced months in
      `poc/data/`), 25 new tests.
- [x] 2026-11-17 Team and video: demo command `(cd poc && python3 -m steadpoc.demo)`,
      from ETA updates to alert, to stock match with a reason for every refused lot, to
      a one-page term sheet. Text on screen, `--html out/demo.html` for a self-contained
      page, `--arrival YYYY-MM-DD` for calendar dates, `--delay 4` for the no-alert
      path. 30 new tests. Simulation now borrows the September 2026 figures (50.6%,
      6.65 days), as the brief does.
