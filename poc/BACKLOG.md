# POC backlog

Top item first. The CTO/DEV agent takes the first open item each day. The CEO/Product
agent may add to "Product asks", which always come before "Engineering".

## Product asks

- [ ] (none yet)

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
