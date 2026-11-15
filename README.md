# stead.ai

Insured stock swaps that keep factories running through shipping delays.

This private repo is the working home of stead.ai. Two AI agents work in it every day:

- **CEO/Product agent** keeps the short pitch deck and the 2-page brief current. It
  proposes changes as pull requests; nothing in the pitch materials changes until Udi
  approves.
- **CTO/DEV agent** builds and tests the proof of concept of the stock-swap engine.

| You want | Open |
|---|---|
| The short deck | `docs/deck/stead.ai_Stock_Swap_Pitch_Deck_Short.pptx` |
| The 2-page brief | `docs/brief/stead.ai_Stock_Swap_Brief_2pages.pdf` |
| What the agents did | `agents/LOG.md` |
| Proposed changes waiting for approval | the Pull requests tab |
| What the POC does next | `poc/BACKLOG.md` |
| The rules the agents follow | `CLAUDE.md`, `agents/` |

To run things yourself:

```
pip install -r requirements.txt
python3 -m pytest poc -q
(cd poc && python3 -m steadpoc)
python3 docs/brief/build_brief.py
python3 tools/check_docs.py
```

Fonts in `docs/brief/fonts` (Inter, Space Grotesk) are under the SIL Open Font License.
