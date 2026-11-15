# POC backlog

Top item first. The CTO/DEV agent takes the first open item each day. The CEO/Product
agent may add to "Product asks", which always come before "Engineering".

## Product asks

These three come from `agents/LLOYDS_LAB_SCORECARD.md` and close gaps a Lab reviewer
will score.

- [ ] Programme: data audit for the weeks 1 to 3 backtest. Write `poc/DATA_AUDIT.md`:
      every dataset the backtest needs (vessel or container tracking history, carrier
      schedules, schedule reliability, delay causes), where it can be had, price,
      licence, and a fallback. State plainly what can be done with public data only.
      Then make a backtest run end to end with no mentor or syndicate data at all.
      Why: reviewers mark down plans that hinge on data the Lab is unlikely to have.
- [ ] Team and video: one command that walks the worked case on screen, from ETA
      update to alert, to stock match, to a one-page term sheet (who lends what, when,
      fee, yield, premium), readable by an underwriter. Output as text and as a
      self-contained HTML page. Why: proof the team can build it, and the demo for
      the application video.
- [ ] Product: price the long stop. From a stated delay distribution, estimate the
      chance the late boxes pass the long-stop date and the premium that implies, with
      the method and assumptions written out, and compare with the $16,000
      placeholder. Why: shows the Lloyd's market what it would be underwriting.

## Engineering

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
- [ ] Command line tool: booking plus ETA updates in, alert, match and a one-page term
      sheet out.

## Done

- [x] 2026-11-15 Seed: economics of the worked case, alert rule, same-grade matching,
      simulated end-to-end run, 14 tests.
