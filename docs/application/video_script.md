# stead.ai video for the Lloyd's Lab Cohort 18 application

Draft by the CEO agent, 2026-11-19, for Udi's approval. Udi records it; the agents do
not produce video. Target: under 5 minutes (the Lab's FAQ asks for a video under 5
minutes). The spoken text below is about 660 words, which runs about 4 minutes 25
seconds at a calm 150 words a minute, leaving room for pauses on the demo.

Serves all three criteria: Team (two founders on camera, a working proof of concept
shown, not described), Product (one concrete swap, the Lloyd's use case in plain
words), Programme (the 10-week ask, read as co-design).

Rules for recording: say only what is written here, or check a change against the
house rules in `CLAUDE.md`. Never say or show that any insurer, syndicate, distributor
or customer is committed. Call the long-stop cover "proposed" every time. The demo
runs on illustrative data and every figure in it is an assumption: say so on screen
and out loud. Do not read the demo's "Method estimate" as a price.

## Shot list and script

Timings are cumulative and approximate. "Slide N" means the short deck,
`docs/deck/stead.ai_Stock_Swap_Pitch_Deck_Short.pptx`.

### 1. The hook (0:00 to 0:25). Udi on camera, plain background

> A factory in Europe is waiting for forty containers of plastic resin. Twelve days
> before they are due, the boxes are moved to a later ship. They will now arrive eleven
> days late, and the plant holds five days of stock. Often, the same resin, same
> producer, same grade, is already sitting in a warehouse at the destination port.
> I'm Udi Bahat, CEO of stead.ai. Our mission is to keep factories running when
> shipping runs late.

Caption on screen: "Illustrative case. Assumptions, not data."

### 2. The gap for the market (0:25 to 1:05). Slide 2 full screen, Udi in voice-over

> Here is the gap for the insurance market. A standard cargo policy excludes loss
> caused by delay, even when an insured peril caused the delay. That is Clause 4.5 of
> the Institute Cargo Clauses. So the factory carries the loss, and the cargo
> underwriter has nothing to sell and no lever to pull. Parametric delay cover, such
> as Otonomi's, now pays a pre-agreed amount when a delay is measured. That helps,
> and we see it as a complement. But the line still stops. And delay is common: in
> September 2026, only about half of container vessels arrived on time, according to
> Sea-Intelligence.

### 3. What we do (1:05 to 1:45). Slide 3, then slide 4

> stead.ai does three things. We detect: we buy in container tracking and alert only
> when a new arrival date outruns the plant's safety stock. We match: we look for
> identical stock held by a distributor at the port. And we make the deal safe. The
> plant can buy that stock outright, or borrow it, and when the late boxes land they
> go to the distributor to repay the loan. Nothing is turned around at sea. Everything
> happens in port, with procedures that run today, such as digital container release
> in Rotterdam.

### 4. The demo (1:45 to 3:00). Screen recording of the proof of concept

Command, run from the `poc` folder: `python3 -m steadpoc.demo`. Use a large terminal
font. Keep the first line, "ILLUSTRATIVE CASE: assumptions, not data", in view for
two seconds. Pause on each point below.

> This is our working proof of concept, running one swap on mock data. Here are the
> tracking updates. Two days late, four days late: no alert, because five days of
> stock cover it. Then the boxes are rolled to a later ship, eleven days late, and the
> engine raises an alert: the line would stop for six days.
>
> Next, the match. The engine reads distributor stock and turns down every lot that
> is not a true substitute: a different grade code, the wrong port, a different
> producing plant, too small, or free too late. It gives a reason for each one. One
> lot fits, and it is chosen.
>
> Finally, a one-page term sheet for the plant, the distributor and the underwriter:
> the dates, what the lender earns, our fee, and what makes the return leg safe. The
> long-stop cover is marked proposed, and its premium is a placeholder, not a price.

Pause points on screen: the ALERT line; the line ending "chosen" among the refused
lots; the term sheet sections "COST OF THE SWAP" and "WHAT MAKES THE RETURN LEG SAFE".

Optional 10 seconds, if time allows: run `python3 -m steadpoc.demo --delay 4`.

> And when stock covers the delay, it stays silent. No alert, no cost.

### 5. What is in it for syndicates (3:00 to 3:35). Slide 5, then slide 6

> For a syndicate there are two things. On delays past a trade disruption deductible,
> the swap could be a mitigation expense instead of a stoppage claim. Our worked case
> sits below the deductible, so there the plant pays. Below it, there is one new risk, the long stop:
> the late boxes arriving far later than agreed. That is the cover we want to word and
> price with you. All of these figures are assumptions, and the premium per swap is
> small. We say so.

Caption on screen: "Worked case: assumptions, not data. Proposed cover; no capacity is
committed."

### 6. Team (3:35 to 4:00). Udi on camera; Ronit on camera if she records a line

> We come from the loss side of payments. I led risk products at PayPal, in fraud
> detection and trust and safety. Ronit Oren, our CTO, has a PhD from Cornell, where
> she also developed algorithms, and nearly six years leading product at Wix. What you
> just saw, we have already built.

If Ronit records her own line, she says the second sentence in the first person
instead, and Udi drops it.

### 7. The ask (4:00 to 4:35). Slide 10, then Udi on camera to close

> In the ten weeks of the Lab, we want to extend our backtest on real vessel arrivals,
> draft the long-stop wording with underwriters and counsel, define the risk feed an
> underwriter would use, and walk one late Rotterdam shipment through every step on
> paper. That is why we want to join: to co-design the wording and pricing with the
> people who would underwrite it, and to interview underwriters, brokers and their
> insured plants through the Lab's network. Not sales. We both work on this full time, and
> our goal is a lead syndicate alongside us by Demo Day. Thank you.

End card, 3 seconds: "stead.ai. Insured stock swaps that keep factories running
through shipping delays."

## Facts said out loud, and their sources (opened 2026-11-19)

| Line | Source |
|---|---|
| Cargo policy excludes loss caused by delay, even if an insured peril caused it (Clause 4.5) | Institute Cargo Clauses (A) 1/1/09, https://www.acerislaw.com/wp-content/uploads/2020/06/Cargo-Clauses-A.pdf |
| Otonomi's parametric cover "pays a pre-agreed amount on defined, measurable events" | Reinsurance News, 9 Oct 2026, https://www.reinsurancene.ws/otonomi-tag-n-trac-solent-freight-services-launch-parametric-cargo-coverage/ |
| About half of vessels on time in September 2026 (50.6%) | Sea-Intelligence via FreshPlaza, 29 Oct 2026, https://www.freshplaza.com/asia/article/9887399/global-shipping-schedule-reliability-improves-to-50-6-in-september/ |
| Digital container release in Rotterdam (Secure Chain, PIN codes retired) | Portbase, 4 Mar 2025, https://www.portbase.com/en/?p=19439 |
| Video under 5 minutes | Lloyd's Lab FAQ, https://www.lloyds.com/insights/lloyds-lab/faqs (as recorded in the scorecard) |
| Demo output | `poc/steadpoc/demo.py`, run 2026-11-19; illustrative data |
| Worked case ($68,000, over $1M) | Slide 6 and `poc/steadpoc/economics.py`; assumptions |
| Team lines | Slide 9, as Udi supplied them |

Left out on purpose: the trade disruption deductible in days (the sources could not
be re-opened today, so the script says only "a trade disruption deductible"), Marsh's
limits and triggers (Marsh's page could not be opened today), and any market size
(not yet sourced).

## Before recording: checks for Udi

1. Re-run the demo the day you record; if its wording changed, re-read section 4
   against the screen.
2. If a newer Sea-Intelligence month is out, update the September figure in section 2
   and on slide 2 together.
3. Read the script aloud once with a timer. If it runs over 4:45, cut the optional
   `--delay 4` segment first, then the last sentence of section 3.
