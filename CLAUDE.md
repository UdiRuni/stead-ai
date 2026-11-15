# stead.ai: shared rules for every agent working in this repo

stead.ai is a pre-seed venture: insured stock swaps that keep a factory running when
its inbound shipment is late. We buy delay early warning, find identical stock in a
distributor's bonded warehouse at the destination port, and make the deal safe: the
plant buys the stock outright, or borrows it and the late boxes repay the loan, with a
proposed long-stop cover on the return leg. Team: Udi Bahat (CEO), Ronit Oren, PhD
(CTO). First target: Lloyd's Lab Cohort 18 (applications open 9 Dec 2026, close
17 Jan 2027). Udi is also looking at other pre-seed accelerators.

Two agents run here every day, each in a fresh session with no memory:

- CEO/Product agent: charter in `agents/CEO_PRODUCT.md`
- CTO/DEV agent: charter in `agents/CTO_DEV.md`

The repo is the only memory. Read `agents/LOG.md` first, write to it last.

## What lives where

| Path | What | Who changes it |
|---|---|---|
| `docs/deck/stead.ai_Stock_Swap_Pitch_Deck_Short.pptx` | The short pitch deck (the only deck we maintain) | CEO agent, by pull request |
| `docs/brief/brief.json` | All text of the 2-page brief | CEO agent, by pull request |
| `docs/brief/build_brief.py` | Layout of the brief; builds the PDF | Either agent, by pull request |
| `docs/brief/stead.ai_Stock_Swap_Brief_2pages.pdf` | Built output, always rebuilt from brief.json | Never edited by hand |
| `docs/archive/` | Frozen originals, including the full deck | Nobody |
| `poc/` | Proof-of-concept code, tests and backlog | CTO agent, directly on main |
| `tools/check_docs.py` | House-rule checks for deck and brief | Either agent |
| `agents/LOG.md` | Shared run log, newest entry on top | Both, directly on main |

## Approval rule

Udi approves every change to the pitch materials. Anything under `docs/` goes on a
branch and into a pull request; never push it to `main`. Keep at most one open pull
request per agent: if yours is still open, add to it instead of opening another.
POC code, the backlog and the log go straight to `main`, and only when all tests pass.

## House rules for the pitch materials

1. No em dashes, anywhere.
2. Never mention Lodestar. The early-warning layer is bought in or built here.
3. No Lloyd's capacity, approval, partner or customer is committed today. Never write
   or imply otherwise. The cover is always "proposed".
4. Illustrative figures are assumptions, not data, and are labelled as such. Output of
   `poc/steadpoc/simulate.py` is simulated and must never be presented as a result.
5. Every factual claim has a source you opened and read today. If you cannot verify a
   claim, soften it or remove it; do not keep it on trust. No invented numbers.
6. Keep the limits honest: the "What we do not claim" section stays.
7. Do not claim that nobody else does this. Otonomi (with Marsh), FourKites and
   project44 are named competitors. The supported wording is "we found no one else who...".
8. The brief is exactly 2 pages. The short deck is at most 10 slides.
9. Keep the existing design. Change words and numbers, not layout, fonts or colours,
   unless Udi asked for a design change.
10. The worked case (40 TEU, $1.2M, 11 days late, 5 days of stock, $68,000 swap) is
    encoded in `poc/steadpoc/economics.py` and tested in `poc/tests/test_worked_case.py`.
    Deck, brief and code must always agree. Change all three together or none.

## Git and pull requests in agent sessions

- Start of a run: attach the repo with push access (the add_repo tool), then
  `git clone https://github.com/UdiRuni/stead-ai` and work in the clone.
- Push with `git -c push.negotiate=true push origin BRANCH`. A "push negotiation
  failed" warning is harmless.
- `gh pr create`, `gh pr list` and `gh pr view` do not work here (no GraphQL). Use REST:
  - list open pull requests: `gh api "repos/UdiRuni/stead-ai/pulls?state=open"`
  - open one: `gh api repos/UdiRuni/stead-ai/pulls -f title="..." -f head=BRANCH -f base=main -f body="..."`
  - read review comments: `gh api repos/UdiRuni/stead-ai/pulls/N/comments` and
    `gh api repos/UdiRuni/stead-ai/issues/N/comments`
- Never merge a pull request and never force-push `main`.
- If a push or pull request is refused, do not work around it. Say so in your final
  report, with the exact error, and stop.

## Things no agent does

No applications, forms, emails, messages or posts. No contact with any company or
person. No spending. No change to repository visibility or settings. Research, write,
build, test and report only.

## Commands

```
pip install -r requirements.txt        # add --break-system-packages if pip asks
python3 -m pytest poc -q               # POC tests
(cd poc && python3 -m steadpoc)        # simulated end-to-end run
python3 docs/brief/build_brief.py      # rebuild the 2-pager from brief.json
python3 tools/check_docs.py            # house-rule checks on deck and brief
```

## Log format (`agents/LOG.md`, newest on top)

```
## YYYY-MM-DD  CEO/Product | CTO/DEV
- Did: what changed, with commit or pull request link
- Found: facts worth keeping, each with a source link
- For CEO / For CTO: anything the other agent must act on
- Needs Udi: decisions only he can make (or "nothing")
```
Keep entries short. When the log passes about 60 entries, fold the oldest into one
summary paragraph at the bottom.
