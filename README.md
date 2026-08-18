# Serie A Scout Index

**A descriptive ranking model for Serie A 2025/26 players.**

## → [Open the site](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/)

---

The TPI ranks qualified Serie A players by attacking impact: xG and xA adjusted for
opponent difficulty, seven dimensions, one ranking. It is **descriptive** — it ranks,
it does not predict — and the checks say where it loses too.

| Page | What it is |
|---|---|
| [Homepage](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/) | What the index is, who is on top right now |
| [Ranking](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/dashboard_serie_a.html) | Every qualified player, five contexts, head-to-head |
| [Validation](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/validazione.html) | What holds up and what does not, with confidence intervals |
| [Method](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/guida_completa.html) | Every formula the engine actually runs |
| [TPI Pro](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/dashboard_pro.html) | The index with the five scout modulators |

**Seven dimensions** — output, buildup, centrality, team boost, consistency, finishing,
recent form. **Five scout modulators** on top of them, in the Pro version: age, physical
durability, cross-context stability, form direction, early momentum. **Five contexts** —
overall, home, away, vs top six, vs the tightest defences.

Numbers are deliberately not repeated here: they live on the pages, which are generated
from the data, so nothing in this file can go stale behind them. The validation page
reports every check exactly as it came out, including the one built to fail the index.

---

### Ask the model — *not live on the published site*

The repository ships an AI assistant that answers questions about the rankings and the
methodology, grounded in the project's own numbers. **It is switched off on the site
above**: it needs a Cloudflare Worker to hold the API key server-side, and no Worker is
deployed, so `WORKER_URL` in `ai_chat.js` is still a placeholder and the widget stays
hidden. Nothing to try on the live pages — this section describes code, not a feature
you can use as a visitor.

| File | Role |
|---|---|
| `ai_chat.js` | The widget. Self-contained, bilingual IT/EN, no API key in the page. Hides itself while `WORKER_URL` is unset. |
| `build_ai_dataset.py` | Builds `ai_dataset.json` from `payload.json`. `--check` fails if the dataset is behind the payload. |
| `ai_dataset.json` | Top 100 players, methodology and validation figures. Generated, never hand-edited — the Worker fetches it over HTTPS. |
| `validazione_sintesi.json` | The headline numbers of the 15 checks, written by the validation run. |
| `worker/` | Cloudflare Worker holding the API key server-side. See [`worker/README.md`](worker/README.md) for the one-time deploy. |

Every fact the assistant is given comes from the engine: dimensions, weights, formulas
and thresholds travel in the `metodo` block of `payload.json`, the validation figures in
`validazione_sintesi.json`. A GitHub Action re-runs `build_ai_dataset.py --check` on
every push, so the dataset cannot drift behind the numbers on the pages.

To turn the assistant on: deploy the Worker, then put its URL in the `WORKER_URL`
constant at the top of `ai_chat.js`. The widget appears on its own once that is set.

---

*Raffaele Ciccone · Season 2025/26*
