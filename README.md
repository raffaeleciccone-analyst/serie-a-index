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

### Ask the model

Every page carries an AI assistant that answers questions about the rankings and the
methodology, grounded in the project's own numbers. It won't invent data that isn't in
the dataset.

| File | Role |
|---|---|
| `ai_chat.js` | The widget. Self-contained, bilingual IT/EN, no API key in the page. |
| `build_ai_dataset.py` | Reduces `payload.json` to the compact `ai_dataset.json` the assistant reads. |
| `ai_dataset.json` | Top 100 players + methodology summary. Must be committed — the Worker fetches it over HTTPS. |
| `worker/` | Cloudflare Worker holding the API key server-side. See [`worker/README.md`](worker/README.md) for the one-time deploy. |

After deploying the Worker, put its URL in the `WORKER_URL` constant at the top of
`ai_chat.js`. Until then the widget stays hidden.

---

*Raffaele Ciccone · Season 2025/26*
