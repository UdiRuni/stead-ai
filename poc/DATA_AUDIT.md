# Data audit for the weeks 1 to 3 backtest

Written 2026-11-16 by the CTO/DEV agent. Every source below was opened on that date.
Pages were read through a text-extraction tool, so quoted wording should be checked in
a browser before it is reused in pitch material. "Not stated" means the page we could
open does not say; it does not mean the answer is no. Nobody was contacted and no
quote was requested, so every "price on request" is still an open question.

## The short answer

1. The backtest now runs end to end with no mentor, syndicate or purchased data:
   `(cd poc && python3 -m steadpoc.backtest)`. It replays 23 months of public monthly
   figures (June 2024 to September 2026, five months skipped, see section 3).
2. What is public and free is market-level: how many vessels were late each month and
   by how much on average. That is enough to show how the engine's workload moves
   with real conditions.
3. What is not public anywhere we looked: shipment-level history with the originally
   scheduled arrival and each later ETA change. That is what a true replay of the
   early-warning rule needs, and we found no source that sells 24 months of it at a
   published price.
4. So the honest wording for the plan is: weeks 1 to 3 run on public data from day
   one; shipment-level tracking history and any mentor claims data make the backtest
   sharper, but the plan does not depend on either.

## 1. What the backtest needs

| # | Dataset | Why the backtest needs it |
|---|---|---|
| A | Schedule reliability: share of arrivals late and how late, by month | Sets how often a delay happens and how long it is |
| B | Actual vessel arrivals at the destination port | Ground truth for "the boxes were late" |
| C | Scheduled arrival as first promised (carrier schedule) | Delay is actual minus scheduled; without it there is no delay |
| D | ETA revision history per shipment or vessel | Measures how many days of warning there really were |
| E | Causes of delay with dates (canal, congestion, strike, weather) | Explains clusters of delay; needed to price a long stop later |
| F | Plant safety stock and distributor stock at the port | Decides whether a delay matters and whether a swap is possible |
| G | Delay claims from a syndicate | Would show what delays cost insured plants |

F comes from customers and distributors, not from any data vendor: it stays an
assumption until interviews or a stock feed replace it. G is the data a Lab reviewer
is right to doubt; nothing in the POC needs it.

## 2. Where each dataset can be had

### A. Schedule reliability

| Source | What it gives | Price | Licence | Link |
|---|---|---|---|---|
| Sea-Intelligence press releases | Global on-time share each month; average delay of late vessel arrivals in most months | Free | No licence or terms found on the release pages | https://www.sea-intelligence.com/press-room/ |
| Sea-Intelligence Global Liner Performance report | Monthly report and Excel file: more than 12,000 vessel arrivals a month, 60+ carriers, 34 trade lanes | "Subscriptions start at 2,000 Euro/Year for 12 monthly issues" | "unrestricted sharing within the subscribing company"; use outside it not stated | https://www.sea-intelligence.com/services |
| Xeneta (eeSea data) | Reliability against the original carrier schedule, at port-pair, service and vessel level; 7,000+ vessels and 50,000+ arrivals a month | Not stated (demo) | Not stated | https://www.xeneta.com/about-us/our-data/reliability |

In use today: the press-release figures, in `poc/data/schedule_reliability_monthly.csv`.
Fallback if they stop: none is needed for past months; the file is in the repo.
Limits: global and vessel-level, not Asia to North Europe and not containers. We found
no free monthly trade-lane series. Sea-Intelligence does not define "on time" on any
page we could open.

### B. Actual vessel arrivals

| Source | What it gives | Price | Licence | Link |
|---|---|---|---|---|
| NOAA and BOEM Marine Cadastre AIS | Vessel positions at one-minute intervals in US waters, files from 2009 onward | Free | "CC0 1.0 Universal public domain dedication" | https://github.com/ocm-marinecadastre/ais-vessel-traffic |
| Danish Maritime Authority AIS | Raw AIS from Danish shore stations, CSV | Free | No licence on the page; how far back the archive goes not verified | https://www.dma.dk/safety-at-sea/navigational-information/ais-data |
| Norwegian Coastal Administration AIS | Norwegian waters, from August 2017 | Free, may need registration | Norwegian Licence for Open Government Data 2.0 | https://www.kystverket.no/en/sea-transport-and-ports/ais/ais-norge/ |
| IMF PortWatch | Daily port-call counts for 2,065 ports and 28 chokepoints. Counts per port, not per vessel | Free | Not readable today; check by hand before relying on it | https://portwatch.imf.org/pages/data-and-methodology |
| Port of Los Angeles | Daily container vessels at anchor, at berth and departed; yearly files | Free | No terms on the file | https://www.portoflosangeles.org/Business/Operations |
| US Bureau of Transportation Statistics | Monthly average container vessel dwell, top 25 US ports, January 2019 to June 2023 | Free | US government work | https://catalog.data.gov/dataset/monthly-average-container-vessel-dwell-times-at-the-top-25-u-s-container-ports-januar-2023 |
| VesselFinder Port Calls API | Arrival and departure times by port or vessel. History depth not stated | 175 EUR per 5,000 credits, 2 credits per record | Terms page could not be opened | https://www.vesselfinder.com/port-calls-api |
| Kpler (MarineTraffic) | "Query up to five years of port call history on demand" | Not stated (demo) | Not stated | https://www.kpler.com/solutions/derived-insights/port-call-trends |
| Port of Rotterdam, Port of Hamburg | Expected and current calls on a web page; no history or download | Free | Not stated | https://www.portofrotterdam.com/en/up-to-date-information/arrival-and-departures |
| Port of Antwerp-Bruges PortVoyages and PortStays API | Ocean-going vessel calls; history depth not readable | Free with sign-in | Terms not readable | https://www.portofantwerpbruges.com/en/our-port/digital-products/open-data-platform/portvoyages-api |

Free per-vessel arrival times exist for US, Danish and Norwegian waters only. For
Rotterdam and Antwerp, free data gives daily counts (PortWatch) but not per-vessel
arrival times; those have to be bought (VesselFinder is the only published price) or
collected from now on (Antwerp API).

### C. Scheduled arrivals

| Source | What it gives | Price | Licence | Link |
|---|---|---|---|---|
| Carrier schedule APIs on the DCSA standard (Maersk, MSC, Hapag-Lloyd, CMA CGM) | Forward schedules only; no page offers past schedules | Mixed; mostly not stated | Maersk's API terms bar the user to "license, sell, aggregate, analyse, rent, lease, transfer, assign, distribute" and to use the data "to build a competitive product or service" | https://terms.maersk.com/node/266 |
| Xeneta (eeSea data) | Arrivals measured against the original carrier schedule | Not stated | Not stated | https://www.xeneta.com/product/eesea |
| Sea-Intelligence custom data | Data "since January 2012" | Price on inquiry | Not stated | https://www.sea-intelligence.com/services |

No free archive of past schedules was found. This is the hard gap: with public data
alone we can see when a ship arrived but not when it was first promised.

### D. ETA revision history

| Source | What it gives | Price | Licence | Link |
|---|---|---|---|---|
| Vizion API | Container tracking; lists "Historical change log" and, on the Professional plan, historical tracking by master bill of lading. How far back is not stated | Core plan: the page shows both $119 and $399 a month. Professional: "Contact us for pricing" | Not stated | https://www.vizionapi.com/container-tracking/pricing |
| Terminal49 | ETA changes pushed as they happen, forward only | Free for up to 10 active containers; otherwise not published | Terms bar building "a competitive product or tool with similar functionality" | https://terminal49.com/pricing |
| Shipsgo | Live tracking only: "the historical data is not available for now" | "500 credits for $1000", one credit per shipment | Not stated | https://shipsgo.com/pricing |
| Portcast | Tracking with predicted ETA; keeps original and latest carrier ETA. Past history not stated | $45,000 per 12 months on its AWS Marketplace listing | Terms could not be opened | https://aws.amazon.com/marketplace/pp/prodview-qfvxj56hpmtue |
| project44 | Full tracking history for shipments the customer creates; retention not stated | Not stated | Not read | https://developers.project44.com/guides/shippers/visibility/ocean/p2p/tracking-updates |

Tracking APIs follow a container from the day it is subscribed. None states that it
can hand back the ETA changes of shipments that sailed two years ago, and all need
real container or bill of lading numbers, which only a shipper or forwarder has.
FourKites could not be opened.

### E. Causes of delay

| Source | What it gives | Price | Licence | Link |
|---|---|---|---|---|
| IMF PortWatch | Daily transits through 28 chokepoints (Suez, Bab el-Mandeb, Panama and others) | Free | Not readable today | https://portwatch.imf.org/pages/data-and-methodology |
| Panama Canal Authority monthly summary | Daily arrivals, transits, waiting time, lock outages with dates | Free PDF | Not stated | https://pancanal.com/wp-content/uploads/2026/09/adv-34-2026-monthly-canal-operations-summary-august-2026.pdf |
| World Bank and S&P Container Port Performance Index | Time container ships spend in port, by port, yearly | Free | CC BY 3.0 IGO | https://openknowledge.worldbank.org/entities/publication/87d77e6d-6b7b-4bbe-b292-ae0f3b4827e8 |

We found no free, dated, structured list of strikes or weather events.

## 3. What runs today on public data only

`poc/steadpoc/backtest.py` reads `poc/data/schedule_reliability_monthly.csv` (28
months, each row with its source link and retrieval date) and runs the engine once
per month with that month's published on-time share and average lateness.

- Public inputs: the two monthly figures.
- Simulated: each shipment and its delay (exponential shape around the published
  mean), safety stock, warning lead time, distributor stock. These are the
  assumptions in `steadpoc/simulate.py`.
- Skipped: February to June 2025. The releases for those months do not state the
  average delay, and we do not interpolate.
- Known weakness: at 1,000 simulated shipments a month, random noise is of the same
  size as some month to month moves. The trend across calm and rough months is clear
  (tested with 20,000 shipments); single months are not.

What this shows: the engine runs on data that exists, and its alert volume follows
real market conditions. What it does not show: that real alerts would have come early
enough, or that identical stock would have been at the port.

## 4. Steps up from here, cheapest first

| Step | Adds | Data | Cost | Open risk |
|---|---|---|---|---|
| 1. Done | Workload against real monthly conditions | Press-release figures | Free | No stated licence for the figures; we store two numbers a month with attribution |
| 2. Free, about a week of work | Real per-vessel arrival and waiting times at a US port, with PortWatch and canal data as warning signals | Marine Cadastre AIS (CC0), PortWatch, Panama Canal summaries | Free | A US proof, not Rotterdam or Antwerp; measures lateness against a vessel's usual pattern, not against the carrier schedule |
| 3. Low cost | Trade-lane and carrier reliability instead of one global number | Sea-Intelligence report | From 2,000 EUR a year | Whether a 12-issue subscription includes past months is not stated |
| 4. Quote needed | Vessel-level scheduled against actual, 24 months | Xeneta (eeSea) or Sea-Intelligence custom data | On request | Price, history depth and licence all unknown |
| 5. Quote needed, plus a shipper | Shipment-level ETA revision history | Vizion Professional, project44 or Portcast, with a plant's or forwarder's past bill of lading numbers | On request | No vendor states past ETA revisions can be recovered; may only be collectable going forward |
| 6. Start now, free | Our own ETA revision archive from today | Terminal49 free tier (10 containers) or the Antwerp API | Free | Needs real container numbers; terms on competitive use need a legal read |

Steps 1 and 2 need nothing from the Lab. Steps 4 and 5 are where a Lab mentor could
help most: not with claims data, but with an introduction to a shipper or forwarder
whose past bookings can be replayed.

### Step 2 progress, 2026-11-21

- Built: `steadpoc/portcalls.py`, the extractor. It reads Marine Cadastre AIS CSV or
  ZIP files, keeps reports inside a port's anchorage and berth boxes, groups them
  into port calls, and gives arrival, first moored time, waiting time, and lateness
  against each vessel's own earlier calling interval (no look-ahead). Calls cut off
  by the data window are flagged and left out of the figures. Tested on invented
  reports only (`tests/test_portcalls.py`).
- Blocked: from the agent sandbox on 2026-11-21, coast.noaa.gov, marinecadastre.gov,
  hub.marinecadastre.gov and the Azure blob store with the GeoParquet files
  (ocmgeodatastor1.blob.core.windows.net) all returned a proxy refusal or no
  connection. Only the GitHub readme could be read
  (https://github.com/ocm-marinecadastre/ais-vessel-traffic, CC0 confirmed there).
  So no real AIS file has been run yet.
- Still to do: a real port definition (boxes drawn from a chart or 33 CFR Part 110,
  with the source in the file), check the column names on a real file, run a month
  at one port, commit the derived call list (CC0 allows it), then feed real waiting
  and lateness into the backtest and the long-stop tail.

## 5. Not verified today

- Sea-Intelligence's definition of "on time" (a secondary source cites plus or minus
  one calendar day from a 2019 methodology).
- IMF PortWatch licence and start date; Danish AIS archive depth.
- Terms of use for VesselFinder, Portcast and Vizion.
- FourKites, Spire, Linerlytica and the Kiel Trade Indicator could not be opened.
