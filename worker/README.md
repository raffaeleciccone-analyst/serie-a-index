# Worker AI — Serie A Scout Index

Proxy fra la dashboard pubblicata su GitHub Pages e la Claude API. Serve a una cosa
sola: **tenere la chiave API lato server**. Il browser parla solo con il Worker, che
aggiunge il dataset al prompt, applica i limiti e ristreamma la risposta.

```
browser (ai_chat.js)  ──POST /chat──>  Worker  ──Messages API──>  Claude
        <──SSE text/event-stream──          │
                                            └──GET ai_dataset.json (cache 1h)
```

## Deploy (una volta sola)

```bash
cd worker
npm install
npx wrangler login
npx wrangler secret put ANTHROPIC_API_KEY     # incolla la chiave, non finisce mai in git
npx wrangler deploy
```

`wrangler deploy` stampa l'URL, tipo
`https://serie-a-scout-ai.<tuo-subdominio>.workers.dev`.
Mettilo in `ai_chat.js` (costante `WORKER_URL`) e ripubblica le pagine.

Verifica: `curl https://serie-a-scout-ai.<tuo-subdominio>.workers.dev/health`

## Tetto giornaliero (consigliato)

Il rate limit per IP ferma i burst, non la spesa. Per un tetto vero:

```bash
npx wrangler kv namespace create QUOTA
```

Copia l'`id` che stampa, incollalo in `wrangler.toml` sotto `[[kv_namespaces]]`,
togli il commento al blocco e rifai `deploy`. Il tetto sta in `DAILY_LIMIT`.

Vale comunque la pena impostare anche un **budget mensile** nella console Anthropic:
è l'unico limite che non dipende da codice tuo.

## Configurazione

Tutto in `wrangler.toml`, sezione `[vars]`:

| Var | Cosa fa |
|---|---|
| `ALLOWED_ORIGINS` | Origini che possono chiamare il Worker. Lista vuota = tutte (solo locale). |
| `DATASET_URL` | Dove il Worker scarica `ai_dataset.json`. Cache 1h. |
| `MODEL` | `claude-opus-5` di default. `claude-sonnet-5` o `claude-haiku-4-5` costano meno. |
| `EFFORT` | `low`/`medium`/`high`/`xhigh`/`max`. Alza se le risposte sono superficiali. |
| `DAILY_LIMIT` | Tetto giornaliero globale (serve il binding KV `QUOTA`). |

Il secret `ANTHROPIC_API_KEY` si imposta con `wrangler secret put`, mai in `[vars]`.

## Costo

Il grosso del prompt è il dataset (~56 KB, ~20k token) ed è **identico a ogni
richiesta**: sta in un unico blocco `system` con `cache_control`, quindi dalla
seconda domanda in poi viene letto dalla cache a un decimo del prezzo. È il motivo
per cui il dataset lo scarica il Worker e non il browser — se ogni client mandasse
il proprio contesto, la cache non aggancerebbe mai.

Il tetto per risposta è `MAX_TOKENS = 2000` in `src/index.js`: basta per una risposta
in chat e mette un limite duro alla parte cara (output).

Per vedere se la cache sta agganciando: `npx wrangler tail` e guarda gli usage nei
log, oppure la dashboard Anthropic (`cache_read_input_tokens` deve essere > 0 dalla
seconda richiesta).

## Aggiornare il dataset

Quando rigeneri la stagione:

```bash
python build_ai_dataset.py     # dalla root del repo demo
git add ai_dataset.json && git commit && git push
```

Il Worker non va ridistribuito: rilegge il file entro un'ora (o subito, al primo
isolate nuovo).

## Sviluppo locale

Crea un file `.dev.vars` (già in `.gitignore`) con dentro una riga
`ANTHROPIC_API_KEY` valorizzata con la tua chiave, poi:

```bash
npx wrangler dev
```

Punta `WORKER_URL` in `ai_chat.js` a `http://localhost:8787` mentre provi.

## Note

- La risposta è SSE con eventi `{type:"text"|"done"|"refusal"|"error"}`.
- I fallback lato server (`fallbacks: "default"`) sono attivi: se il classificatore
  di sicurezza rifiuta per falso positivo, la richiesta viene rigiocata su un modello
  di ripiego dentro la stessa chiamata invece di tornare vuota. Per disattivarli,
  togli `betas` e `fallbacks` da `params` in `src/index.js`.
- Il dataset è passato al modello dentro `<dataset>` con l'istruzione esplicita di
  trattarlo come dati e non come comandi.
