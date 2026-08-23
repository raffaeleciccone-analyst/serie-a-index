# Serie A Scout Index

**A descriptive ranking model for Serie A 2025/26 players.**

## → [Open the site](https://raffaeleciccone-analyst.github.io/serie-a-index/)

---

The TPI ranks qualified Serie A players by attacking impact: xG and xA adjusted for
opponent difficulty, seven dimensions, one ranking. It is **descriptive** — it ranks,
it does not predict — and the checks say where it loses too.

Where it loses, precisely: against three elementary predictors, the TPI beats none of the
three on the **level** of future output. On the question it was built for — *who will improve
on himself* — it beats two of the three, with the confidence interval entirely above zero.
Both results are on the [validation page](https://raffaeleciccone-analyst.github.io/serie-a-index/validazione.html)
in full, because an index that has never lost is only an index that has never been tested.

| Page | What it is |
|---|---|
| [Homepage](https://raffaeleciccone-analyst.github.io/serie-a-index/) | What the index is, who is on top right now |
| [Ranking](https://raffaeleciccone-analyst.github.io/serie-a-index/dashboard_serie_a.html) | Every qualified player, five contexts, head-to-head |
| [Validation](https://raffaeleciccone-analyst.github.io/serie-a-index/validazione.html) | What holds up and what does not, with confidence intervals |
| [Method](https://raffaeleciccone-analyst.github.io/serie-a-index/guida_completa.html) | Every formula the engine actually runs |
| [TPI Pro](https://raffaeleciccone-analyst.github.io/serie-a-index/dashboard_pro.html) | The index with the five scout modulators |
| [Data (CSV)](https://raffaeleciccone-analyst.github.io/serie-a-index/serie_a_tpi_2025-26.csv) | All 351 qualified players, 49 columns, written by the engine on every run |

**Seven dimensions** — output, buildup, centrality, team boost, consistency, finishing,
recent form. **Five scout modulators** on top of them, in the Pro version: age, physical
durability, cross-context stability, form direction, early momentum. **Five contexts** —
overall, home, away, vs top six, vs the tightest defences.

The ranking page publishes the top 100 by default and loads **all 351 qualified players** on request — the top-100 cut is not a neutral filter, it favours the teams that produce most, so the list was dense with Inter and Milan and nearly empty of Cremonese and Lecce. Players beyond the hundred come without the per-matchday series, and the page says so.

The ranking page also exports what you are looking at: filter the list, hit **CSV**, and you get those rows in that order. The link next to it is the full file above.

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
