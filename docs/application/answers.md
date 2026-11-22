# Draft application answers, Lloyd's Lab Cohort 18

Draft by the CEO agent, 2026-11-20, for Udi's approval. Nothing here is submitted by an
agent. Udi submits, after his own review.

## Read this first

- **The questions below are our guess, not the real form.** We looked for the Cohort 17
  form questions and did not find them in public. The Lab's FAQ says only that you
  submit "your details via the application form"
  (https://www.lloyds.com/lloyds-lab/faqs). Sonr's Cohort 17 page and the Cohort 16
  information handbook list themes, dates and the three criteria, but no questions
  (https://sonr.global/lloyds-lab/,
  https://www.enterprise-ireland.com/documents/lloyd-s-lab-accelerator-cohort-16-information-handbook-pdf-en-172386.pdf).
  So the questions are built from the three criteria and the sub-points in the scoring
  guidance hosted by Sonr (undated, not on lloyds.com; see the scorecard). When the
  Cohort 18 form opens on 9 Dec 2026, the CEO agent maps these answers onto the real
  questions the same day.
- **Facts are the ones already in the merged deck and brief,** with the same sources.
  Those sources could not be re-opened today (fetch refused), so every figure must be
  re-checked before Udi submits. Sources opened today are marked "(opened 2026-11-20)".
- **Gaps are left blank on purpose.** Where only Udi knows the answer (commitment,
  funding, company details, interviews), the answer says `[Udi: ...]`. We do not fill
  these in.
- Answers are kept to about 150 words each, since we do not know the limits.

## Facts about the Lab worth keeping in mind (opened 2026-11-20)

- The Lab selects "approximately 10 teams from 150-200 global applications", and runs
  two cohorts a year
  (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).
- Cohort 18 dates are unchanged: open 9 Dec 2026, close 17 Jan 2027, shortlist 5 Feb,
  Pitch Day 10 Mar, Welcome Week 19 Apr, Demo Day 23 Jun 2027 (same page). Cohort 18
  themes are not published yet.
- The Cohort 16 handbook says "Insurance experience not required. We care about
  problem-solving, not pedigree." That is an earlier cohort's document, so we do not
  quote it in the answers, but it suggests our Team gap is about evidence of the work,
  not about CVs.
- No equity is taken (FAQ, above).

---

## Company basics

**Q. Company name, website, country, stage, funding to date.**

stead.ai. Pre-seed, pre-revenue. `[Udi: website, country of incorporation, whether
incorporated yet, funding to date if any]`

**Q. Describe your company in one sentence.** (Product)

stead.ai keeps a factory running when its shipping containers run late: we spot the
delay early, find identical stock in a distributor's warehouse at the destination
port, and make the deal safe with a proposed long-stop cover on the return leg.

**Q. What is your mission and vision?** (Product)

Mission: keep factories running when shipping runs late.

Vision: stock on call at the port, on terms agreed before the delay. The cure for a
late shipment is often already in a warehouse at the same port. What is missing is an
early warning, a view of that stock and a safe way to borrow it. Insurance can supply
the third, and gain what no delay cover has today: a way to stop the loss, not only to
pay for it.

North star: factory stoppage days avoided per insured plant, per year. It is the one
number the plant, the lender and the syndicate all care about.

**Q. Who is it for, and what does each party get?** (Product: suitability to the
Lloyd's market)

| Who | What they get | Stage |
|---|---|---|
| A plant that imports a commodity grade by sea and holds thin stock | Warned early, it buys or borrows identical stock at the port, so the line keeps running | In the Lab: one insured swap, arranged when the alert fires |
| A distributor with bonded stock at the port | A yield on idle stock, with the return leg covered by the proposed long stop | In the Lab |
| A marine cargo or trade disruption underwriter | A new short-duration premium line (the long stop) and, past the deductible, a lever that can make a stoppage claim smaller | Wording and pricing co-designed in the Lab |
| The plant's broker | A standing swap line: a proposed yearly add-on to the cargo policy, with grades, lenders and the long-stop price agreed before any delay | Next, after the Lab. Direction, not built |
| Underwriters pricing delay | Records of how late boxes really ran and how deep port stock was, which we could not find for sale | Later, only with volume |

We start with the plant, because without a plant that wants the swap there is no
deal, and with the underwriter, because the Lab is where the wording and price get
made. Only the single swap runs in our proof of concept, on mock data.

**Q. Which Lab theme does this fit?** (Product)

Cohort 18 themes are not out yet. Cohort 17's "new products" theme asked for
"solutions which address supply chain disruption"
(https://www.lloyds.com/insights/lloyds-lab/cohort-17). We are a new product for that
gap, with active loss mitigation for trade disruption books as a second use.
`[CEO agent: replace with the Cohort 18 theme wording on 9 Dec]`

---

## Product: does it solve a problem or create an opportunity for the Lloyd's market?

**Q. What problem are you solving?** (Product: suitability to the Lloyd's market)

A standard cargo policy pays nothing for delay: Institute Cargo Clauses, Clause 4.5,
excludes it even when an insured peril caused it. Trade Disruption Insurance starts
after a delay deductible of typically 30 days, reducible to 14, on named perils only.
In September 2026 only 50.6% of vessels arrived on time, and late vessels were 6.65
days late on average (Sea-Intelligence). So a plant with five days of stock and a
shipment 11 days late carries the whole stoppage itself. Parametric delay cover now
exists (Marsh, built with Lab alumnus Otonomi, up to $250,000), but it pays cash after
the line stops. Nothing keeps the line running, and below the deductible an
underwriter has nothing to sell that does.

Sources: as in the brief (ICC (A); Miller; Sea-Intelligence via FreshPlaza; Marsh;
Lloyd's Lab alumni page).

**Q. What is your product and how does it work?** (Product)

1. Detect: we buy container-level tracking (for example FourKites, project44 or Kpler)
   and compare each new arrival estimate with the plant's safety stock. We alert only
   when the delay outruns it, about 12 days before the scheduled arrival (a target).
2. Match: we find stock of the same producer, plant and grade code in the bonded
   warehouse of one of 3 to 5 distributors at the port.
3. Clear: the plant buys that stock outright, or borrows it. On a loan, the distributor
   releases it by digital delivery order on the original date; when the late boxes
   arrive they go, still under customs suspension, into the distributor's customs
   warehouse and repay the loan. Duty and VAT are paid once.

The plant's cargo policy already covers loss of the late boxes and General Average.
The one new risk is that the boxes arrive far later. The proposed long-stop cover pays
an agreed value if they pass an agreed date.

**Q. Why is this new, and who else is doing it?** (Product: innovation)

Others warn, pay out or sell stock. FourKites and project44 warn, without stock or
cover. Marsh and Otonomi pay after the line stops. Air freight moves only part of a
40-container shipment at high cost. Buying spot works if the plant has cash and space
for double stock. We found no one else who finds identical stock before the line stops
and makes both routes safe: an outright purchase, or a loan the late boxes repay. We do
not build the warning; our part is the match and the safe deal.

**Q. What is in it for the Lloyd's market?** (Product)

Two things, both proposed, neither committed. First, a new short-duration delay line:
the long-stop cover on the return leg. In our illustrative case the premium is a
$16,000 placeholder on a $1.2M swap; our proof of concept shows a first pricing method
that lands near it in the base case but ranges from under $2,000 to over $100,000 as
the long-stop date and the delay tail change, which is exactly what we want to set with
underwriters. Second, smaller trade disruption claims: on delays that run past the
deductible, the syndicate could fund a swap as a mitigation expense instead of paying a
stoppage claim. Our illustrative 11-day case sits inside a typical deductible, so there
the plant pays the $68,000 itself, against a loss of up to $1.08M. All figures are
assumptions, not data.

**Q. How big is the market?** (Product: market size)

We have not sized it, and we will not pretend to. Our first market is polypropylene
imports into Europe through Rotterdam and Antwerp, projected above 2 million tonnes for
2025 (ChemOrbis, in the product case). On our own assumptions, each 1% of
worked-case-sized shipments becoming a swap is about 40 swaps a year, about $640,000 of
premium. That is a pilot-sized book. The larger case is the standing swap line (a
proposed yearly add-on to the plant's cargo policy) and other graded inputs, and
neither is proven. Finding how many thin-stock importers exist is a goal of our
interviews. `[Udi: replace with interview findings or a broker's view if you have one]`

**Q. What is the business model?** (Product)

On a $1.2M swap in our illustrative case the plant pays $68,000: $28,000 to the lender
(about 77% annualized simple yield), $16,000 premium (placeholder) to the syndicate,
and a $24,000 fee to stead.ai (2.0% of notional). Arranging cover is regulated, so
stead.ai would act under a broker or coverholder.

---

## Team: do you have the skills and commitment to do what you claim?

**Q. Who is on the team and why are you the people to build this?** (Team: relevant
experience, quality of work)

Udi Bahat, CEO: lead PM for risk products at PayPal until October 2026 (fraud detection,
trust and safety on AI and ML), over 20 years in fintech, telecom, mobile security and
retail, M.Sc. Computer Science, Reichman University, cum laude. Ronit Oren, PhD, CTO:
Cornell PhD and algorithm developer there, then nearly six years leading product at
Wix (Head of Product for the Wix CMS platform, GM of Wix Multilingual, Wix Stores).

We come from the loss side of payments: pricing and stopping losses in real time on
noisy signals. Built so far: a working proof of concept, on mock data, that runs one
swap from alert to stock match to term sheet, a backtest on 23 months of public
schedule data, and a first pricing and accumulation method for the long stop.

What we lack is marine cargo and trade disruption experience. We say so, and it is the
first thing we want from the Lab's mentors. `[Udi: add named advisors only if they have
agreed]`

**Q. How committed are you to the programme?** (Team: commitment)

Udi Bahat, our CEO, works on stead.ai full time. `[Udi: Ronit's time commitment, from
when, and whether you can both attend the London weeks.]`

**Q. Have you spoken to customers or the market?** (Programme: traction within the
insurance industry)

Not yet. In the Lab we plan more interviews with underwriters, brokers and insured plants
met through mentors. `[Udi: number of interviews held by submission, with whom by role (plant,
distributor, underwriter, broker), and one finding each. If none, say "planned: 12 to
15 interviews" and the date of the first.]`

---

## Programme: would your plan work at the Lloyd's Lab?

**Q. What will you do in the 10 weeks?** (Programme: realistic and achievable plan,
product development focus)

- Weeks 1 to 3, backtest: extend our backtest, which replays 23 months of public
  schedule data today, with real vessel arrivals. Mentor data is a bonus, not a need.
- Weeks 4 to 6, wording: draft the long-stop extension with counsel (insurable
  interest, loss payee, long-stop date, eBL control) for LMA and JCC review.
- Weeks 7 to 8, integration: define the stock feed and the risk score API underwriters
  would use. A proposed stock feed format and a sample feed (invented data) exist
  today; a distributor's real feed is an upgrade if one joins.
- Weeks 9 to 10, paper pilot: walk a late Rotterdam shipment through every step with
  mentors, no goods moved, and scope a facility or MGA binder.

**Q. What do you need from the Lab?** (Programme)

Co-design, not customers. That is why we want to join. We want a marine cargo or trade
disruption underwriter and a claims lead to shape the wording and the pricing method
with us, and a specialty broker to tell us how it would be placed. We also want to
interview underwriters, claims teams, brokers and their insured plants met through
mentors, to test the problem with the market before we build further. These are
research interviews, not sales calls. We recruit the distributor ourselves; none is a
partner yet.

**Q. What does success look like at Demo Day?** (Programme)

A draft long-stop wording reviewed by mentors, a pricing method underwriters have
corrected, a backtest that states warning lead time on real arrivals, a paper pilot
walked end to end, and a scoped facility or MGA binder. No capacity is committed today.

**Q. What are the biggest risks?** (all three)

Demand is unproven: plants often hold about 30 days of stock, and sellers carry delays
on delivered terms. Stock depth at the port is unmeasured until a distributor opens its
data. Quality approval, tax and legal form vary by plant and country. Systemic events,
when the lender's boxes are late too, are out of scope. Accumulation behind one vessel
or event is real; our proof of concept caps exposure per vessel and per event and shows
the loss in a stress scenario, and the limits are for underwriters to set.

---

## What Udi needs to supply before submission

1. Company details: website, country, incorporation, funding to date.
2. Commitment: one true sentence on time and attendance.
3. Interviews: how many, with whom, one finding each, or the honest plan.
4. Advisors: names only if they have agreed.
5. Re-check of every figure against its source on the day you submit.
