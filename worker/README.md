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

Prova prima il Worker da solo, senza browser — isola quasi tutti i problemi:

```bash
curl -N -X POST http://localhost:8787/chat \
  -H "Content-Type: application/json" \
  -H "Origin: https://raffaeleciccone-analyst.github.io" \
  -d '{"messages":[{"role":"user","content":"Chi è primo nel TPI e perché?"}],"lang":"it"}'
```

L'header `Origin` serve: senza, rispondo 403 perché `ALLOWED_ORIGINS` è valorizzato.

Poi il widget: punta `WORKER_URL` in `ai_chat.js` a `http://localhost:8787` e
aggiungi **temporaneamente** `http://localhost:8787` alla `connect-src` della
pagina che stai provando — la CSP permette solo `https://*.workers.dev`, quindi
in locale il browser blocca la fetch. Servi le pagine con un server vero
(`python -m http.server 8000`), non da `file://`.

## Usare un altro fornitore

Il Worker ha un secondo percorso che parla **formato OpenAI**
(`POST /chat/completions`). Non è legato a un fornitore: lo parlano OpenAI,
Mistral, Groq, DeepSeek, Together, OpenRouter, xAI, l'endpoint compatibile di
Gemini, e in locale Ollama e LM Studio.

Si attiva valorizzando `COMPAT_API_URL`. Passalo da riga di comando invece di
scriverlo in `wrangler.toml`, così non resta niente da rimettere a posto:

```bash
npx wrangler dev \
  --var COMPAT_API_URL:https://api.mistral.ai/v1 \
  --var COMPAT_MODEL:mistral-large-latest \
  --var COMPAT_API_KEY:...

curl http://localhost:8787/health     # → {"backend":"openai-compat", ...}
```

Su un fornitore vero la chiave va in `wrangler secret put COMPAT_API_KEY`, non
in `--var` e mai in `wrangler.toml`.

Due differenze rispetto al percorso Anthropic, entrambe di costo:

- Lì marco esplicitamente il dataset come cacheable (`cache_control`), ed è da lì
  che viene il grosso del risparmio. OpenAI e Gemini fanno caching automatico su
  prefissi identici, quindi qualcosa recuperi gratis, ma non è la stessa cosa.
- `effort` e i fallback server-side non esistono su questo percorso; il codice
  già non li manda.

### Modelli a contesto piccolo (Ollama, LM Studio)

Stesso percorso, più due parametri. Per il mio Ollama con `num_ctx=4096`:

```bash
npx wrangler dev \
  --var COMPAT_API_URL:http://localhost:11434/v1 --var COMPAT_MODEL:qwen3:14b \
  --var COMPAT_MAX_PLAYERS:10 --var COMPAT_MAX_TOKENS:700
```

Tre cose da sapere, tutte misurate su questo progetto:

- **In locale vale solo con `wrangler dev`.** Un Worker distribuito sull'edge di
  Cloudflare non raggiunge il tuo `localhost`, e i visitatori nemmeno.

- **Il contesto fallisce in silenzio.** Ollama gira di default con `num_ctx=4096`
  e ci riserva dentro anche lo spazio per l'output. Quando il totale sfora, taglia
  il prompt **dall'inizio**: spariscono le istruzioni e i primi giocatori, e il
  modello risponde pescando dalla coda rimasta. Nessun errore, solo una risposta
  plausibile e sbagliata. Misurato: con 10 giocatori e `max_tokens` 2000 usciva il
  4° in classifica al posto del 1°; riducendo l'output a 700 il prompt ci sta e la
  risposta torna esatta (Lautaro, Inter, TPI 1.8, rank 1). Per alzare i valori
  serve prima alzare la finestra: `OLLAMA_CONTEXT_LENGTH=16384` e riavvio.
  **`COMPAT_MAX_PLAYERS` è spento di default**: con un fornitore cloud lascialo
  spento, o l'assistente risponderà "non è nel dataset" su giocatori che ci sono.

- **Serve a provare il giro, non la qualità — e il difetto non è nemmeno
  riproducibile.** Anche con il dataset interamente nel contesto, `qwen3:14b`
  alla domanda "chi è primo nel TPI" ha risposto Lukaku una volta e Calhanoglu
  quella dopo, inventando i punteggi. Alla domanda "qual è il TPI di Donnarumma"
  (che nel dataset non c'è) ha prima risposto correttamente che non è presente,
  elencando i nomi giusti, e a una prova successiva ha inventato **1.227**.
  Stesso modello, stessa domanda, stessa configurazione: esito opposto. Un
  modello piccolo legge la tabella ma poi risponde dal proprio pregiudizio, e
  non lo fa in modo abbastanza costante da poterci nemmeno mettere una pezza nel
  prompt. Usalo per verificare streaming, CORS, rate limit, validazione e
  widget; per giudicare le risposte serve un modello serio.

## Note

- La risposta è SSE con eventi `{type:"text"|"done"|"refusal"|"error"}`.
- I fallback lato server (`fallbacks: "default"`) sono attivi: se il classificatore
  di sicurezza rifiuta per falso positivo, la richiesta viene rigiocata su un modello
  di ripiego dentro la stessa chiamata invece di tornare vuota. Per disattivarli,
  togli `betas` e `fallbacks` da `params` in `src/index.js`.
- Il dataset è passato al modello dentro `<dataset>` con l'istruzione esplicita di
  trattarlo come dati e non come comandi.
