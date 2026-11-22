# stead.ai product case, built on the product framework

Draft by the CEO agent, 2026-11-17, for Udi's approval. It applies the nine-step
framework Udi supplied (clarifying questions, mission, vision, goal and north star,
users, pain points, solutions, tradeoffs, metrics) to stead.ai, as a Lloyd's Lab
reviewer scoring the Product criterion would read it. It feeds the deck's vision
slide, the video script and the application answers.

Rules that bind this file: the cover is always "proposed"; no Lloyd's capacity,
partner or customer is committed; figures marked "assumption" are not data; every
source below was opened on 2026-11-17.

## 1. Clarifying questions

| Question | Answer |
|---|---|
| Who is it for? | Three parties in one deal: a factory with thin stock, a distributor holding identical stock at the port, and the syndicate that insures the return leg. The Lab reviewer reads it as the third. |
| Why build it? | A standard cargo policy pays nothing for delay (Institute Cargo Clauses, Clause 4.5), and trade disruption cover starts after a long deductible. In between, the factory carries the loss and the underwriter has nothing to sell and nothing to do. |
| Why at Lloyd's? | The one new risk, the long stop, needs wording and a price. That is specialty marine work. The Lab's own FAQ asks whether a product solves "a problem or create[s] opportunities for the Lloyd's market" (https://www.lloyds.com/insights/lloyds-lab/faqs). |
| Where first? | Rotterdam and Antwerp, polymers. Port release is digital there and customs rules let goods change hands under suspension (sources in the brief). |
| What is out of scope? | Systemic events, when the lender's own boxes are late too. Mid-ocean title swaps. Any cover on Lloyd's paper today. |

## 2. Mission

Keep factories running when shipping runs late.

Updated 2026-11-22 on Udi's request: the mission now heads deck slide 8 and opens the
brief and the video, and the offering below is stated per user on slide 8 and in the
application answers.

## 3. Vision

Stock on call at the port, on terms agreed before the delay.

Why: the cure for a late shipment is often already in a warehouse at the same port.
What is missing is an early warning, a view of that stock and a safe way to borrow it.
Insurance can supply the third, and get something no delay cover has today: a way to
stop the loss, not only to pay for it.

## 4. Goal and north star

Goal: reduce factory stoppage caused by late inbound shipments, and turn that into a
small new line of premium and smaller trade disruption claims for the market.

North star: **factory stoppage days avoided per insured plant, per year.**

Why this one: it is the only number all three parties care about. The plant counts it
in lost output, the syndicate in claims it does not pay, the distributor in loans it
earns a yield on. Premium and fees follow from it; the reverse is not true.

## 5. Users

| # | User group | What they want | Size of the group |
|---|---|---|---|
| 1 | Supply chain or procurement lead at a plant that imports a commodity grade by sea and holds thin stock | The line does not stop | First market: Europe's polypropylene imports were projected above 2 million tonnes for 2025, more than half from Saudi Arabia and South Korea (ChemOrbis, https://www.chemorbis.com/en/premium-plastics-news/Europe-PP-outlook-for-2026-A-market-in-structural-reset-amid-growing-imports-and-deeper-restructuri/2025/12/05/954179). How many of those buyers hold thin stock is not known; interviews must find out |
| 2 | The plant's risk manager and its broker | A delay answer they can buy | Not sized |
| 3 | Distributor with bonded stock at the port | Yield on idle stock, with a safe return leg | Named targets in the brief; none is a partner |
| 4 | Marine cargo or trade disruption underwriter | A delay risk that can be priced, and a lever on the loss | The reviewer. Global cargo premium is in the deck (IUMI) |
| 5 | Claims lead on a trade disruption book | A cheaper outcome than a stoppage claim | Not sized |

Priority for demand: group 1. Without a plant that wants the swap there is no deal.
Priority for the Lab: group 4. The Lab can help with wording and pricing method, and
mentors can lead us to underwriters, brokers and their insured plants for research
interviews that test the problem. We do not ask the Lab for customers or distributors.

### The offering, per user (2026-11-22)

| User | Offering | Stage |
|---|---|---|
| Plant with thin stock (group 1) | Warned early, buys or borrows identical stock at the port; the line keeps running | Now: one insured swap (solution A) |
| Distributor (group 3) | Yield on idle stock, return leg covered by the proposed long stop | Now (A) |
| Underwriter (group 4) | A new long-stop premium line; past the deductible, a lever on the claim | Co-designed in the Lab |
| Broker and risk manager (group 2) | A standing swap line to place each year | Next (solution B) |
| Underwriters pricing delay (groups 4 and 5) | Delay and stock-depth records | Later (solution C) |

Honest note on size. A sized market is part of the Product score in the scoring
guidance we found (hosted by Sonr, not Lloyd's, undated). We can size the first market
by arithmetic only, on assumptions: at about 12 tonnes per TEU (assumption), 2 million
tonnes is about 4,000 shipments of the worked-case size a year. Each 1% of them that
became a swap would be about 40 swaps, about $640,000 of premium at the $16,000
placeholder. That is an illustration of scale, not a forecast, and it is small. The
honest answer to "how big" is: one grade in one region is a pilot-sized book; the
market case rests on the standing line in section 7 and on other graded inputs, and
neither is proven.

## 6. Pain points

For the underwriter (group 4):

| # | Pain point | How often | How painful | Evidence |
|---|---|---|---|---|
| 1 | Past the deductible, a delay claim cannot be made smaller. There is no physical lever | Rare | High: a stopped large plant is costly. Siemens puts unplanned downtime at $36,000 an hour in consumer goods and $2.3 million an hour at a large car plant (True Cost of Downtime 2024, https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/TCOD-2024_original.pdf). Those are general downtime figures, not delay claims | No underwriter has told us this yet |
| 2 | Below the deductible there is nothing to sell that keeps the line running. Parametric delay cover pays cash after the stop | Frequent: about half of vessels were late in September 2026 (Sea-Intelligence, in the brief) | Medium per event | Published policy terms, in the brief |
| 3 | Delay cannot be priced well: shipment-level delay history is not for sale at a published price | Constant | Medium | `poc/DATA_AUDIT.md` |
| 4 | Accumulation: many insureds behind one late vessel or one event | Rare | High | Our own reasoning; not yet modelled |

For the plant (group 1): the line stops (rare, severe); air freight moves only part of
the load at high cost; buying spot needs cash and storage for double stock; insurance
pays late or not at all.

Priority: pain point 2 for the underwriter, paired with "the line stops" for the plant.
It is the frequent one, it is where no product exists that prevents the stop, and it is
where a small new premium line can be written. Pain point 1 is the bigger number per
event but needs a covered named-peril claim, so it is the second act, not the first.

A broader signal that cover and concern are out of line: a WTW study of 1,000 firms
with revenue above $250 million finds wide gaps between what firms worry about in
their supply chains and what they insure, and notes that many disruptions "do not
result in direct physical loss where the policy expects to see it"
(https://www.wtwco.com/en-gb/insights/2026/05/mind-the-gap-what-1000-executives-reveal-about-supply-chain-insurance-misalignment).
It does not measure delay, so it supports the direction, not our numbers.

## 7. Solutions

| # | Solution | Solves | Cost to build | Scales? |
|---|---|---|---|---|
| A | **One insured swap.** Warning bought in, identical stock matched, the plant buys or borrows, the proposed long stop covers the return leg. Arranged when the alert fires | Pain 2, and the plant's stoppage | Lowest: wording, a price, one distributor | Slowly. Each deal is set up under time pressure, 8 to 12 days out |
| B | **Standing swap line.** A proposed annual add-on to the plant's cargo policy. Grades, quality approval, distributors, the long-stop date and its price are agreed in advance. When an alert fires, the swap binds in hours | Pain 2 again, and removes our three biggest limits: lead time, quality approval and thin premium per deal | Medium: needs A to have worked at least on paper | Yes: premium recurs each year and is not earned only when a delay happens |
| C | **Delay data for pricing.** Every alert and swap records how late boxes really ran and how deep port stock was. Offered to underwriters to price delay below the deductible, and to pair with parametric cover, whose payout could fund a swap | Pain 3 | Low once A or B runs; nothing before | Yes, but only with volume |

MVP: A. It is the smallest thing that tests the two unknowns that matter, whether
identical stock is really at the port and whether a lender accepts the proposed cover.
It is what the Lab's ten weeks are planned around.

Next: B. It is the product a broker can place and a syndicate can budget for. We
present it as direction, not as something built.

Later: C, and the mitigation route above the deductible (pain point 1).

The journey, for solution A: the plant's booking number is entered once. Each new
arrival estimate is compared with the plant's safety stock. Twelve days out the delay
outruns the stock and an alert fires. The matcher lists identical lots at the port and
says why each other lot was refused. A one-page term sheet shows lender, goods, dates,
yield, premium and fee. The plant accepts; the distributor releases stock on the
original date; the late boxes repay it. All of this runs today in the proof of concept
on invented data: `(cd poc && python3 -m steadpoc.demo)`.

What the syndicate would underwrite: `(cd poc && python3 -m steadpoc.longstop)` shows
a first pricing method. If the boxes pass the long-stop date the cover pays the agreed
value and the insurer takes over the boxes, so its net loss is a share of the value,
not all of it. On an exponential delay tail around the public 6.65 days, a long stop
at T+30 and a 15% net loss (assumptions), the method gives about $17,000 against our
$16,000 placeholder. It also shows how fragile that is: from under $2,000 with a long
stop at T+45 to over $100,000 at T+21 with a fatter tail. That spread is the point:
the long-stop date and the tail are what we ask underwriters to set with us. It is a
method, not a quote, and accumulation is not in it yet.

## 8. Tradeoffs

| Tradeoff | Workaround |
|---|---|
| Lead time. A swap arranged at the alert needs 8 or more days; some delays show later | The standing line (B) moves the slow steps to before the delay |
| Stock depth is unmeasured | Start with grades distributors hold in volume; measure with the first distributor's data |
| Premium per swap is small | We say so. The standing line makes it annual; the mitigation route makes the saving, not the premium, the prize |
| Accumulation and systemic events | Single-shipment delays only; per-vessel and per-event limits; systemic events excluded. To be worded with underwriters |
| Quality approval can block a swap | Same producer, plant and grade only; approval done in advance under B |
| Arranging cover is regulated | stead.ai would act under a broker or coverholder |
| The warning is bought in, so it is not ours to defend | Our part is the match and the safe deal; any tracking vendor can feed it |

## 9. Metrics

North star: factory stoppage days avoided per insured plant, per year.

| Kind | Metric | Where it comes from |
|---|---|---|
| Adoption | Plants enrolled; distributors sharing a stock feed | Pilot |
| Warning quality | Share of alerts given 8 or more days ahead; false alerts per 100 | Backtest, then pilot |
| Match | Share of alerts with identical stock at the port | First distributor's data |
| Conversion | Alerts that become a bound swap | Pilot |
| Underwriting | Share of swaps that pass the long stop; loss ratio of the long-stop cover; premium per insured plant | Pilot, with underwriters |
| Value | Stoppage cost avoided per $1 of swap cost; trade disruption claim avoided where covered | Pilot |
| Satisfaction | Would the plant and the distributor do it again | Interviews |

For the ten weeks at the Lab the measures are narrower: a backtest that states warning
lead time on real arrivals, a draft long-stop wording reviewed by mentors, a pricing
method underwriters have corrected, and a paper pilot walked end to end.

## What still keeps Product below 5

A 5 means every part is shown with evidence. Three parts are not, and no document
closes them:

1. **Demand.** No plant has said it wants this. Needs interviews.
2. **A market voice.** No underwriter has said the problem or the cover is real to them.
   One attributable line would do more than any slide.
3. **Size.** Only the arithmetic above. A distributor's or broker's view of how many
   thin-stock importers exist would replace it.
