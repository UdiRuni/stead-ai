# Data files

## schedule_reliability_monthly.csv

Global container liner schedule reliability, one row per data month, June 2024 to
September 2026 (28 months).

- Source: Sea-Intelligence press releases on its Global Liner Performance report. Each
  row carries the link to the release it was read from. Retrieved 2026-11-16.
- `on_time_pct`: share of vessel arrivals on time, as first published for that month.
- `avg_delay_late_days`: average delay of LATE vessel arrivals, in days. Empty for
  February to June 2025: the releases for those months do not state it, and we do not
  fill gaps by interpolation.
- These are vessel arrivals, not shipments or containers, and global, not a trade lane.
- Figures are as first published. Sea-Intelligence revises earlier months, so month on
  month changes quoted in later releases do not always chain.
- The pages were read through a text-extraction tool. Before any figure from this file
  goes into pitch material, open the linked release in a browser and check it.
- Licence: the press releases carry no licence or terms of use that we could find. We
  store only the two headline numbers per month, with attribution and a link. This is
  not the paid report or its data file (those may only be shared inside the
  subscribing company). If the repo is ever made public, review this file first.

## sample_stock_feed.csv

ILLUSTRATIVE stock feed in the proposed format (`poc/STOCK_FEED.md`). Every lot is
invented: the same seven lots as the demo's built-in stock, so the demo gives the same
match when it reads this file. It is not stock of any real distributor. Written by us,
free to share.
