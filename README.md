# Serie A Scout Index

**Data-driven player ranking model for Serie A 2025/26**

---

## 🔗 [→ Open Homepage](https://raffaeleciccone-analyst.github.io/serie-a-scout-demo/homepage.html)

---

A model designed to evaluate and rank Serie A players using independent performance metrics —
corrected for opponent difficulty, stabilized with Bayesian Shrinkage,
validated against real outcomes with Bootstrap confidence intervals.

---

### 6 independent KPIs
Output Adj/90 · Centrality · Team Boost · Consistency · Age Index (AII) · Physical Reliability (PRI)

### Statistically validated
Predictive backtest Spearman ρ = 0.70 · Bootstrap 95% CI · Kendall τ ranking stability

### 5 contexts of analysis
Total · Home · Away · vs Top 6 · vs Strong Defenses

---

### 🤖 Ask the model

Every page carries an AI assistant that answers questions about the rankings and the
methodology, grounded in the project's own numbers — TPI, per-dimension z-scores,
contexts, form, age. It won't invent data that isn't in the dataset.

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
