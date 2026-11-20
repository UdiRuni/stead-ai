# Stock feed format (proposal)

Status: proposal, built 2026-11-20. No distributor sends us a feed today. This is the
format we would bring to the Lab's weeks 7 to 8 ("define the stock feed ... on a sample
feed"), to be checked with distributors and changed where they need it.

The sample feed `poc/data/sample_stock_feed.csv` is ILLUSTRATIVE: invented lots, the
same ones the demo uses, not real stock of any company.

## Why these fields

A swap only works with stock the plant's QA has already approved. QA approves a
producer, a producing plant and a grade code, so a lot needs all three, plus where it
sits and when it is free. Nothing else is read. A distributor does not have to tell us
price, customer or cost to take part in a match.

## Columns

One header row, then one lot per row. Comma separated, UTF-8 (a byte order mark from a
spreadsheet export is accepted). Column order is free; names are lower case.

| Column | Required | Meaning | Rule |
|---|---|---|---|
| `lot_id` | yes | The distributor's own reference for the lot | Unique in the feed |
| `distributor` | yes | Who holds the stock and would lend it | Not empty |
| `producer` | yes | Producer, as on the QA approval | Compared exactly |
| `plant` | yes | Producing plant, as on the QA approval | Compared exactly |
| `grade` | yes | Grade code | Compared exactly |
| `port` | yes | Port where the stock sits | Compared exactly |
| `teu` | yes | Whole TEU in the lot | Whole number, 0 or more |
| `available_on` | column yes, value may be blank | Day the lot is free to release | YYYY-MM-DD; blank means free now |
| `snapshot_date` | yes | Day the feed was taken | YYYY-MM-DD, the same on every row |

Lines that start with `#` are comments. Extra columns are allowed and ignored, with a
warning, so a distributor can send its usual export.

## What the parser checks

`(cd poc && python3 -m steadpoc.stockfeed FEED.csv [--match-date YYYY-MM-DD])`

It lists every problem with its line number in one pass, and a feed with any error
gives no lots at all: we never match against half a feed.

Errors: no header; a missing or repeated column; a row with too many or too few values;
an empty required value; TEU that is negative, a fraction or not a number; a date that
is not YYYY-MM-DD; a repeated `lot_id`; more than one snapshot date; a snapshot dated
after the match day; a quoted value running over two lines.

Warnings (the feed is still used): extra columns; a lot of 0 TEU; a header with no
lots; a snapshot more than 1 day older than the match day (an assumption: older stock
may already be sold).

Days until a lot is free are counted from the match day, the day we search, not from
the snapshot. A lot free on or before the match day counts as free now.

## Use it in the demo

`(cd poc && python3 -m steadpoc.demo --stock-feed data/sample_stock_feed.csv)` reads
the stock from the file instead of the built-in list. With `--arrival YYYY-MM-DD` the
match day is T-10 of that date; without it, the feed's snapshot date.

## Open questions for distributors (not solved here)

- Real stock is counted in tonnes or bags, not TEU. We need their unit and a
  conversion they agree with.
- Whether the lot is in a customs warehouse or already in free circulation changes the
  paperwork of a loan. We do not ask for it yet because we have not checked the customs
  rule for each case.
- Lots already promised to a customer: does the feed leave them out, or flag them?
- How often a feed can be sent (daily, or on request when an alert fires).
