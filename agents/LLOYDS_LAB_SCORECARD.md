# Lloyd's Lab Cohort 18 scorecard

The goal of this repo until 17 Jan 2027: get stead.ai accepted into Lloyd's Lab
Cohort 18. Every application is read by several reviewers and scored on three
criteria: team, product and programme. Clear writing scores better, and a short video
(under 5 minutes) and a pitch deck (about 10 slides or fewer) normally help.
Source: criteria as shared by Udi on 2026-11-15, from the Lab's FAQs
(https://www.lloyds.com/insights/lloyds-lab/faqs). The CEO agent re-reads that page
weekly and updates this file if the criteria change.
Re-read 2026-11-16: criteria unchanged (team, product, programme; video under 5 minutes
and/or a deck of broadly 10 or fewer slides; no equity taken). Cohort 18 themes are not
published yet. Cohort 17 themes were operational efficiency, new products and
experimental innovation; "new products" asks for "solutions which address supply chain
disruption" (https://www.lloyds.com/insights/lloyds-lab/cohort-17). That is our theme.
The accelerator page promises mentors, market access and pilots with syndicates; it does
not mention data (https://www.lloyds.com/insights/lloyds-lab/programmes-and-initiatives/lloyds-lab-accelerator).

Re-read 2026-11-23: accelerator page dates unchanged, still no Cohort 18 themes, no
attendance terms stated. The FAQ page could not be opened from the agent today, so the
criteria are carried over unchanged, not re-confirmed.

Re-read 2026-11-20: dates unchanged, no Cohort 18 themes yet; the Lab selects "approximately 10 teams from 150-200 global applications" (accelerator page).

Dates: applications open 9 Dec 2026, close 17 Jan 2027, shortlist 5 Feb 2027,
Pitch Day 10 Mar 2027, Welcome Week 19 Apr 2027, Demo Day 23 Jun 2027 (confirmed on the
accelerator page 2026-11-16). Target: application ready for Udi's final review by 5 Jan 2027.

Scoring detail found 2026-11-17 in a "Lloyd's Lab Scoring Guidance" PDF hosted by Sonr
(https://sonr.global/wp-content/uploads/2023/12/Lloyds-Lab-Scoring-Guidance.pdf, linked
from Sonr's Cohort 17 page, https://sonr.global/?p=13687). It is not on lloyds.com and
carries no date, so treat it as a guide, not as the rule. Each criterion is scored 1 to 5.
Team: quality of work, relevant experience, commitment to the programme. Product:
suitability to the Lloyd's market, innovation, market size. Programme: product
development focus, a realistic and achievable 10-week plan, traction within the
insurance industry. Lloyd's staff score every application, the top 40% go to market
mentors, the top 24 pitch, and 10 to 12 are chosen. Two things we do not show at all
today: market size, and traction within the insurance industry.

## How to use this file

Both agents read it every run. The CEO agent owns it and re-scores it every Monday as
a sceptical Lab reviewer would, 1 (weak) to 5 (strong), with one sentence of reasoning.
Every gap has an owner and a next step. A gap the materials can close becomes a pull
request; a gap the POC can close becomes a "Product ask" in `poc/BACKLOG.md`; a gap
only a person can close goes under "Needs Udi" in the log, once, not every day.
Scores must be honest. Do not raise a score without new evidence in the repo.

## 1. Team: do they have the skills and commitment to do what they claim?

Score 2026-11-23: 2 of 5 (unchanged). Both founders full time and a POC demo on mock
data are now on main, but no one with cargo, TDI or distribution experience is named and
no interview has been held, so a market reviewer still sees the domain gap first.

Score 2026-11-16: 2 of 5. Strong risk, product and algorithm backgrounds,
but no one on the team has worked in marine cargo, insurance or chemical distribution,
and the materials still show no advisor, no commitment and no customer contact. The POC
now has a public-data backtest, but no demo yet and it is not in the materials.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| Domain skill in cargo, TDI or distribution | Nothing; deck says two advisors "to recruit" | Largest gap in the application | Udi | Recruit one cargo or TDI underwriting advisor and one polymer distribution advisor; name them in the deck |
| Ability to build it | Bios; a working POC, cited on the team slide and in the brief since 2026-11-18 (pull request 4, merged) | Built by agents under the team's direction; a reviewer may ask who wrote it | CEO | Keep the wording true as the demo changes; mention the POC in the video and application answers |
| Commitment | Both founders full time; London for mandatory weeks and main events, remote between (Udi, 2026-11-22). Proposed in pull request 6 | Partial attendance may read as weaker commitment if Cohort 18 expects more time in London | CEO | Check Cohort 18 attendance terms on 9 Dec; Cohort 16 allowed flexible working with three mandatory London weeks |
| Evidence of customer contact | None done. Pull request 5 proposes first interviews before the Lab and more in the Lab, through mentors (Udi's plan, 2026-11-22) | Plan, not evidence | Udi | Hold a first few interviews before 9 Dec if possible; CEO agent keeps a question list and records findings Udi reports |

## 2. Product: a specific use case for the Lloyd's market, not tech looking for a problem?

Score 2026-11-23: 3 of 5 (unchanged). Pull requests 1, 3 and 5 are merged (plain
language, vision, pricing method, worked-case fixes), so the writing is clearer, but no
plant or underwriter has said they want this and market size is honestly "not yet sized".

Score 2026-11-16: 3 of 5. The use case is specific and fits the Lab's own
"supply chain disruption" wording, but demand is unproven, every figure is an assumption
and the premium is a placeholder. The plain-language pass is proposed in pull request 1,
not yet approved, so it does not count.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| A problem the market recognises | ICC Clause 4.5, TDI deductible, Otonomi and Marsh cover | No voice of an underwriter or plant | Udi | Interviews; one quotable, attributable line would lift this |
| What is in it for Lloyd's | New short delay line, smaller TDI claims | Premium is a placeholder ($16,000) | CTO | First method done 2026-11-17 (`poc/steadpoc/longstop.py`): about $17,000 in the base case, but $2,000 to over $100,000 as the long-stop date and tail change. Not a quote. Next: fitted tail and accumulation limits (backlog). The brief cites the method in pull request 3 |
| Specific, not generic | Worked case, port procedures, wording of the gap | Reads dense to a non-logistics reviewer | CEO, then Udi | Plain-language pass proposed 2026-11-16 in pull request 1; waits for Udi's approval |
| Honest about competitors | "Why we win" table | Must stay current. Willog (cargo monitoring data for parametric cover) is in Cohort 17, so reviewers have just seen a cargo-data pitch | CEO | Daily watch. Decide in the outside-reader test whether to name Willog as a neighbour. FourKites Inventory Twin read 2026-11-17: it moves surplus between the customer's own sites, no outside stock, loan or cover (https://www.businesswire.com/news/home/20260505928982/en/) |

| Vision, north star and market size | Nothing on main | One deal only; no direction, no size | CEO, then Udi | Proposed 2026-11-17 in pull request 3: `docs/application/product_framework.md` on Udi's framework, and a vision slide (swap line, north star, first market). Size stays thin: one grade in one region is a pilot-sized book |

What keeps Product below 5 after pull request 3, and only Udi can close: no plant has
said it wants this, no underwriter has said the problem or the cover is real, and
market size is arithmetic on assumptions. One attributable line from an underwriter
and one from a plant would do more than any further writing.

## 3. Programme: would the 10-week plan work at the Lab?

Score 2026-11-23: 3 of 5 (unchanged). Pull request 2 is merged, so the plan no longer
depends on mentor data or a distributor, but there is still no traction within the
insurance industry, which the scoring guidance names under Programme.

Score 2026-11-16: 3 of 5. The CTO's data audit shows the backtest can run on
public data with no mentor data, which removes the risk in fact, but deck and brief
still carry the old wording, and weeks 7 to 10 still need a distributor we do not have.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| Does not hinge on data the Lab is unlikely to have | Weeks 1 to 3 replay tracking data "plus mentors' delay claims" | Syndicate delay claims data may not be shareable; 24 months of tracking data must be bought or found | CEO, then Udi | CTO part done 2026-11-16 (`poc/DATA_AUDIT.md`, public-data backtest). Rewording proposed 2026-11-17 in pull request 2; waits for Udi's approval |
| Realistic in 10 weeks | Backtest, wording, integration, shadow pilot | Weeks 7 to 10 need a distributor we do not have | Udi and CEO | Paper pilot and sample feed proposed 2026-11-17 in pull request 2, with a distributor as an upgrade. A letter of interest would still lift this; Udi's call |
| Uses the Lab for co-design, not as a sales channel | "Who we want to work with" lists underwriters, claims, brokers | Wording must never read as a request for customers | CEO, then Udi | Co-design wording proposed 2026-11-17 in pull request 2 |
| A clear outcome by Demo Day | Lead syndicate alongside us, facility or MGA binder scoped | Fine | CEO | Keep |

## Application package

| Item | Status | Owner |
|---|---|---|
| Pitch deck, 10 slides or fewer | Have 10 slides, the limit | CEO |
| 2-page brief | Have | CEO |
| Video under 5 minutes | Script and shot list proposed 2026-11-19 in pull request 5 (about 630 words, about 4 min 10 s, includes the POC demo). Waits for Udi's approval, then Udi records | CEO script, CTO demo, Udi records |
| Written answers to the application form | Draft proposed 2026-11-20 in pull request 5 (`docs/application/answers.md`). Cohort 17 questions are not public, so questions are built from the criteria; map to the real form on 9 Dec. Blanks for Udi: company details, commitment, interviews, advisors | CEO, then Udi |
| Clear writing | First outside-reader test 2026-11-21 (section below); plain-language pass still waits in pull request 1 | CEO |
| Market size (Product, per the scoring guidance) | Not shown anywhere. Needs a sourced figure or an honest "not yet sized" | CEO, in the application answers |
| Traction in the insurance industry (Programme, per the scoring guidance) | None. Interviews with underwriters would be the first evidence | Udi |

## Outside-reader test, 2026-11-21

Read cold as a sceptical Lab reviewer: the short deck and the 2-page brief on main, and
the draft answers in pull request 5. The three hardest questions, where we answer them
today, and the gap. Next test: 2026-11-28.

1. **"Why borrow for $68,000 when buying spot costs about $8,000 a month to carry?"**
   (Product: a specific use case.) Our own comparison (deck slide 7, brief "Why we win"
   table) prices "buy spot, with us or direct" at market price plus about $8,000 a month,
   0 days stopped. A reviewer will compare that with the $68,000 loan and ask why anyone borrows.
   Where answered: only "needs cash and storage for double stock". Gap: we never say
   when the loan beats the purchase (cash tied up, no room for double stock, price risk
   on the extra stock, as in the 2026 polypropylene swing the brief already cites), nor
   that stead.ai earns on the purchase route too. Owner: CTO (purchase route economics,
   moved to Product asks today), then CEO to add one line to deck and brief.
   Update 2026-11-22: CTO answered (`poc/steadpoc/purchase.py`): on our assumptions buying
   is cheaper; the loan wins for plants short of cash or room, or avoiding price risk.
   Proposed in pull request 5: the $8,000 labelled as an assumed 8% a year in deck and
   brief, and slide 7 notes say when the loan wins. Waits for Udi.
2. **"In your own worked case, who pays the $68,000?"** (Product: what is in it for
   Lloyd's.) The brief says an 11-day delay "falls inside the TDI deductible", so no TDI
   claim exists. Yet deck slide 5, Pillar A ("above the TDI deductible"), shows "$68k
   instead of a $390k to $1.08M claim", and slide 6 gives the syndicate "avoids the claim
   where covered". In the worked case the plant pays, and the syndicate earns only the
   long-stop premium. A market reviewer will catch this. Where answered: nowhere clearly.
   Gap: wording. Owner: CEO, then Udi. Next step: propose in the next CEO run that Pillar
   A says the $68k figure is the thin-stock case and that the TDI saving applies only to
   delays past the deductible; slide 6 syndicate row to match. No number changes, so
   `economics.py` is untouched.
   Update 2026-11-22: proposed in pull request 5 (slides 5 and 6, notes, answers, video
   script). Waits for Udi.
3. **"Delays cluster. Who carries the long stop when a whole port or route is late, and
   is $16,000 a price?"** (Product: suitability; Programme: realistic plan.) Where
   answered: the brief targets single-shipment delays because in systemic events
   lenders' boxes are late too; the POC has a per-vessel limit and a first pricing method
   ($2,000 to over $100,000 as the long-stop date and tail change, scorecard Product row).
   Gap: the deck shows only the $16,000 placeholder, with no range and no word on
   accumulation limits; there is no book-level limit yet and no sourced event frequency.
   Owner: CTO (accumulation, Engineering backlog; needs a sourced event frequency), then
   CEO adds one line on limits to slide 5 once it exists.

## Status note, 2026-11-23

Pull requests 1 to 7 are all merged. Where a table row above says a change "waits for
Udi's approval", read it as live on main. No open CEO pull request.

## Biggest gap, 2026-11-23 (unchanged since 2026-11-16)

Team: no one with cargo, TDI or distribution experience is named, and no interview has
been held. Only Udi can close it. Everything the agents can write is secondary to this.
