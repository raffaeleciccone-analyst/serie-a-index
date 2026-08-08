# Font

Serviti dal repo invece che da Google Fonts, così le pagine non fanno richieste
a terzi e la CSP può restare `font-src 'self'`.

| File | Famiglia | Origine |
|---|---|---|
| `oswald-latin-var.woff2` | Oswald (variabile, 200–700) | subset latino di `fonts.gstatic.com/s/oswald/v57` |
| `jetbrainsmono-latin-var.woff2` | JetBrains Mono (variabile, 100–800) | subset latino di `fonts.gstatic.com/s/jetbrainsmono/v24` |

Sono file **variabili**: un peso qualsiasi nell'intervallo esce dallo stesso
file, quindi due file coprono tutti i pesi usati. 52 KB in tutto.

Entrambe le famiglie sono sotto **SIL Open Font License 1.1** (`OFL.txt`), che
consente esplicitamente l'auto-hosting. La licenza vale per entrambe; il testo
è quello del progetto Oswald, JetBrains Mono usa la stessa versione.

## Aggiornarli

```
curl -A "Mozilla/5.0" "https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap"
```

e scaricare gli URL `woff2` del blocco `/* latin */`. Se cambia il nome del
file va aggiornato anche `src:url(...)` nelle `@font-face`, che stanno in
`index.html`, `guida_completa.html` e `serie-a-scout-index/assets/dashboard.css`.

`parte2_dashboard.py` copia questa cartella accanto all'HTML generato: le
`@font-face` usano path relativi, senza la copia la dashboard aperta da
`dashboard_output/` ricadrebbe sui fallback di sistema.
