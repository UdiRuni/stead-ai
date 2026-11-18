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

Score 2026-11-16: 2 of 5 (unchanged). Strong risk, product and algorithm backgrounds,
but no one on the team has worked in marine cargo, insurance or chemical distribution,
and the materials still show no advisor, no commitment and no customer contact. The POC
now has a public-data backtest, but no demo yet and it is not in the materials.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| Domain skill in cargo, TDI or distribution | Nothing; deck says two advisors "to recruit" | Largest gap in the application | Udi | Recruit one cargo or TDI underwriting advisor and one polymer distribution advisor; name them in the deck |
| Ability to build it | Bios; a working POC, cited on the team slide and in the brief since 2026-11-18 (pull request 4, merged) | Built by agents under the team's direction; a reviewer may ask who wrote it | CEO | Keep the wording true as the demo changes; mention the POC in the video and application answers |
| Commitment | Not stated | Reviewers cannot tell if this is full time | Udi | Decide what we can truthfully say (full time, hours, start date); CEO agent adds it |
| Evidence of customer contact | "12 to 15 interviews" planned, none done | Plan, not evidence | Udi | Hold interviews before 9 Dec; CEO agent keeps a question list and records findings Udi reports |

## 2. Product: a specific use case for the Lloyd's market, not tech looking for a problem?

Score 2026-11-16: 3 of 5 (unchanged). The use case is specific and fits the Lab's own
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

Score 2026-11-16: 3 of 5 (unchanged). The CTO's data audit shows the backtest can run on
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
| Pitch deck, 10 slides or fewer | Have 9 slides; 10 if pull request 3 is merged, which is the limit | CEO |
| 2-page brief | Have | CEO |
| Video under 5 minutes | Not started. Needs a script, a storyboard and a POC demo to show on screen | CEO script, CTO demo, Udi records |
| Written answers to the application form | Form opens 9 Dec. Draft from the Cohort 17 questions first | CEO |
| Clear writing | Not yet tested on an outside reader | CEO |
| Market size (Product, per the scoring guidance) | Not shown anywhere. Needs a sourced figure or an honest "not yet sized" | CEO, in the application answers |
| Traction in the insurance industry (Programme, per the scoring guidance) | None. Interviews with underwriters would be the first evidence | Udi |

## Biggest gap, 2026-11-16

Team: no one with cargo, TDI or distribution experience is named, and no interview has
been held. Only Udi can close it. Everything the agents can write is secondary to this.
