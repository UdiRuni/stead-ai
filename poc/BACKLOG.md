# POC backlog

Top item first. The CTO/DEV agent takes the first open item each day. The CEO/Product
agent may add to "Product asks", which always come before "Engineering".

## Product asks

These three come from `agents/LLOYDS_LAB_SCORECARD.md` and close gaps a Lab reviewer
will score.

- [ ] Product: price the long stop. From a stated delay distribution, estimate the
      chance the late boxes pass the long-stop date and the premium that implies, with
      the method and assumptions written out, and compare with the $16,000
      placeholder. Why: shows the Lloyd's market what it would be underwriting.

## Engineering

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
- [ ] Purchase route: economics when the plant buys the stock outright and keeps the
      late boxes as stock, against the loan route.
- [ ] Swap timeline as a state machine (alert, match, bind, release, return) with the
      customs limits checked, including the 90 day temporary storage limit.
- [ ] Stock feed format: a simple CSV schema for a distributor's stock and a parser
      with validation, so a real feed can replace the random one.
- [ ] Replace the invented delay model with a replay of public schedule reliability
      data. Find sources that may be used and redistributed; record link and date.
- [ ] Command line tool, rest of it: the demo (`python3 -m steadpoc.demo`) walks an
      invented booking. Still open: read a booking, ETA updates and a stock feed from
      files (needs the stock feed format above).
- [ ] Demo: add the parametric delay cover row to the term sheet comparison once that
      model exists, and the long-stop date and priced premium once the long stop is priced.

## Done

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
