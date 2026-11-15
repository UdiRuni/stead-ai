# Lloyd's Lab Cohort 18 scorecard

The goal of this repo until 17 Jan 2027: get stead.ai accepted into Lloyd's Lab
Cohort 18. Every application is read by several reviewers and scored on three
criteria: team, product and programme. Clear writing scores better, and a short video
(under 5 minutes) and a pitch deck (about 10 slides or fewer) normally help.
Source: criteria as shared by Udi on 2026-11-15, from the Lab's FAQs
(https://www.lloyds.com/insights/lloyds-lab/faqs). The CEO agent re-reads that page
weekly and updates this file if the criteria change.

Dates: applications open 9 Dec 2026, close 17 Jan 2027, shortlist 5 Feb 2027,
Pitch Day 10 Mar 2027. Target: application ready for Udi's final review by 5 Jan 2027.

## How to use this file

Both agents read it every run. The CEO agent owns it and re-scores it every Monday as
a sceptical Lab reviewer would, 1 (weak) to 5 (strong), with one sentence of reasoning.
Every gap has an owner and a next step. A gap the materials can close becomes a pull
request; a gap the POC can close becomes a "Product ask" in `poc/BACKLOG.md`; a gap
only a person can close goes under "Needs Udi" in the log, once, not every day.
Scores must be honest. Do not raise a score without new evidence in the repo.

## 1. Team: do they have the skills and commitment to do what they claim?

Score 2026-11-15: 2 of 5. Strong risk, product and algorithm backgrounds, but no one
on the team has worked in marine cargo, insurance or chemical distribution, and the
materials do not yet show commitment.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| Domain skill in cargo, TDI or distribution | Nothing; deck says two advisors "to recruit" | Largest gap in the application | Udi | Recruit one cargo or TDI underwriting advisor and one polymer distribution advisor; name them in the deck |
| Ability to build it | Bios; a working POC in this repo | POC is not mentioned in the materials | CTO, then CEO | Make the POC demo-ready, then cite it in deck and brief |
| Commitment | Not stated | Reviewers cannot tell if this is full time | Udi | Decide what we can truthfully say (full time, hours, start date); CEO agent adds it |
| Evidence of customer contact | "12 to 15 interviews" planned, none done | Plan, not evidence | Udi | Hold interviews before 9 Dec; CEO agent keeps a question list and records findings Udi reports |

## 2. Product: a specific use case for the Lloyd's market, not tech looking for a problem?

Score 2026-11-15: 3 of 5. The use case is specific (40 TEU, 11 days late, named lines
of business) and the syndicate benefit is stated, but demand is unproven and every
figure is an assumption.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| A problem the market recognises | ICC Clause 4.5, TDI deductible, Otonomi and Marsh cover | No voice of an underwriter or plant | Udi | Interviews; one quotable, attributable line would lift this |
| What is in it for Lloyd's | New short delay line, smaller TDI claims | Premium is a placeholder ($16,000) | CTO | Price the long stop from a delay distribution and show the method |
| Specific, not generic | Worked case, port procedures, wording of the gap | Reads dense to a non-logistics reviewer | CEO | Plain-language pass: a reviewer new to shipping should get it in two minutes |
| Honest about competitors | "Why we win" table | Must stay current | CEO | Daily watch, already in the charter |

## 3. Programme: would the 10-week plan work at the Lab?

Score 2026-11-15: 3 of 5. The plan is concrete and asks for the Lab's real strengths
(wording, underwriters, counsel), but two parts lean on things the Lab may not have.

| Reviewer will look for | What we show today | Gap | Owner | Next step |
|---|---|---|---|---|
| Does not hinge on data the Lab is unlikely to have | Weeks 1 to 3 replay tracking data "plus mentors' delay claims" | Syndicate delay claims data may not be shareable; 24 months of tracking data must be bought or found | CTO | Data audit: for each dataset, where it comes from, cost, licence and a fallback. Make the backtest run with no mentor data at all |
| Realistic in 10 weeks | Backtest, wording, integration, shadow pilot | Weeks 7 to 10 need a distributor we do not have | Udi and CEO | Either secure a distributor's letter of interest before applying, or rescope the pilot to a paper replay that needs none |
| Uses the Lab for co-design, not as a sales channel | "Who we want to work with" lists underwriters, claims, brokers | Wording must never read as a request for customers | CEO | Frame every ask as building market wording and underwriting method together |
| A clear outcome by Demo Day | Lead syndicate alongside us, facility or MGA binder scoped | Fine | CEO | Keep |

## Application package

| Item | Status | Owner |
|---|---|---|
| Pitch deck, 10 slides or fewer | Have 9 slides | CEO |
| 2-page brief | Have | CEO |
| Video under 5 minutes | Not started. Needs a script, a storyboard and a POC demo to show on screen | CEO script, CTO demo, Udi records |
| Written answers to the application form | Form opens 9 Dec. Draft from the Cohort 17 questions first | CEO |
| Clear writing | Not yet tested on an outside reader | CEO |
