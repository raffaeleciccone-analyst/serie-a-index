"""Riduce payload.json al dataset compatto che l'assistente AI legge.

Il Worker Cloudflare scarica ai_dataset.json e lo mette nel system prompt con
cache_control: quindi conta ogni byte. Qui teniamo solo i campi su cui ha senso
fare domande (ranking, contesti, forma, eta, affidabilita) e buttiamo le serie
per-giornata, che valgono migliaia di token e non servono a una risposta in chat.

NIENTE NUMERI SCRITTI A MANO. La metodologia era una costante di testo in questo
file, e mentiva: sei dimensioni invece di sette, l'AII spacciata per dimensione
del TPI quando e' un modulatore del Pro, la consistenza calcolata con l'IQR
(versione rimossa perche' era una dimensione morta), il picco d'eta a 27 anni
quando il motore usa 23, rho 0.70 dove il sito pubblica 0.725, e nessuna
menzione di finishing, che pesa 0.20 ed e' la dimensione che l'ablation indica
come piu' utile. Il file esisteva per impedire all'assistente di inventare, e
gli serviva fatti falsi.

Ora tutto arriva dal motore:
    payload.json           -> blocco "metodo" (dimensioni, pesi, formule, soglie)
    validazione_sintesi.json -> i numeri delle verifiche pubblicate

Uso:
    python build_ai_dataset.py                 # legge payload.json accanto a questo file
    python build_ai_dataset.py path/al/payload.json
    python build_ai_dataset.py --check         # non scrive: fallisce se e' da rigenerare
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "ai_dataset.json"
VALIDAZIONE = BASE_DIR / "validazione_sintesi.json"

# Quanti giocatori esporre. Il payload ne classifica 100; oltre i primi ~60 le
# domande diventano rare e il costo per token resta su ogni singola richiesta.
N_PLAYERS = 100


def r(value, digits=3):
    """Arrotonda se numerico, altrimenti lascia stare (None compreso)."""
    return round(value, digits) if isinstance(value, (int, float)) else value


def compact_player(p: dict) -> dict:
    ctx = p.get("ctx") or {}
    tot = ctx.get("totale") or {}
    kpi = p.get("kpi") or {}
    conv = p.get("conv") or {}
    rank = p.get("rank") or {}
    form = p.get("form") or {}
    recent = p.get("recent") or {}
    phys = p.get("physical") or {}
    tpi = p.get("tpi") or {}

    return {
        "nome": p.get("nome"),
        "squadra": p.get("squadra"),
        "ruolo": p.get("ruolo"),
        # Il ruolo che fa davvero (quinto, mezzala, trequartista) e quanto del
        # suo tempo lo ha passato li'. Serve all'assistente per rispondere a
        # "chi puo' sostituire X", che con ATT/CEN/DIF non si puo' fare.
        "ruolo_specifico": p.get("ruolo_fine"),
        "ruolo_specifico_quota": r(p.get("ruolo_fine_quota"), 2),
        # Il consenso del mercato, in euro. Serve all'assistente per rispondere
        # a "rende piu' di quanto costa?", che e' la domanda che un direttore
        # sportivo fa davvero — ed e' anche la baseline del test Q.
        "valore_mercato_eur": p.get("valore_mercato"),
        # Scadenza contratto: per un direttore sportivo e' la differenza fra
        # "mi piace" e "posso prenderlo".
        "contratto_scadenza": (p.get("contratto") or {}).get("scadenza"),
        "rank": rank.get("TPI"),
        "tpi": r(tpi.get("totale")),
        "tpi_casa": r(tpi.get("casa")),
        "tpi_trasferta": r(tpi.get("trasferta")),
        "tpi_vs_top6": r(tpi.get("vs_top6")),
        "tpi_vs_forti": r(tpi.get("vs_forti")),
        "minuti": r(p.get("minuti"), 0),
        "presenze": tot.get("n_app"),
        "eta": r(phys.get("eta"), 1),
        "eta_cat": phys.get("eta_cat"),
        # Gli z delle SETTE dimensioni del TPI: sono la spiegazione del
        # punteggio, non un extra. Prima ne uscivano cinque piu' AII e PRI, che
        # dimensioni non sono: l'assistente non poteva spiegare una differenza
        # che venisse da finishing o dalla forma, cioe' da 0.31 di peso.
        "z": {
            "output": r(p.get("z_output")),
            "buildup": r(p.get("z_buildup")),
            "centralita": r(p.get("z_centralita")),
            "boost": r(p.get("z_boost")),
            "consistenza": r(p.get("z_consistenza")),
            "finishing": r(p.get("z_finishing")),
            "form": r(p.get("z_form")),
        },
        # Modulatori del TPI Pro, tenuti separati dalle dimensioni.
        "z_pro": {
            "aii": r(p.get("z_aii")),
            "pri": r(p.get("z_pri")),
        },
        "xg90": r(kpi.get("xg_p90")),
        "xa90": r(kpi.get("xa_p90")),
        "goal90": r(kpi.get("goal_p90")),
        "goal": conv.get("goal_tot"),
        "xg": r(conv.get("xg_tot"), 2),
        "sos": r(kpi.get("sos")),
        "forma": recent.get("label"),
        "forma_ratio": r(recent.get("ratio")),
        "forma_trend": r(form.get("trend")),
        "confidence": r(p.get("confidence")),
        "affidabilita": r(phys.get("affidabilita")),
        "infortuni": phys.get("n_infortuni"),
        "acquisto_invernale": bool(p.get("is_winter")),
    }


def metodologia(metodo: dict) -> str:
    """La sintesi del modello, scritta dai pesi che il motore usa davvero.

    Fonte unica: il blocco `metodo` che parte1_analisi.py mette nel payload. Se
    domani un peso cambia o una dimensione sparisce, questa frase cambia con
    lui e nessuno se ne deve ricordare.
    """
    dims = metodo.get("dimensioni") or []
    elenco = "\n".join(
        f"{i}. {d['nome_it']} (peso {d['peso']:.2f}) - {d['formula']}"
        for i, d in enumerate(dims, 1)
    )
    z = metodo.get("z") or {}
    eta = metodo.get("eta") or {}
    shr = metodo.get("shrinkage") or {}
    pro = ", ".join(m["nome_it"] for m in (metodo.get("modulatori_pro") or []))
    contesti = ", ".join(metodo.get("contesti") or [])
    pesi_ruolo = ", ".join(
        f"{k} {v:.2f}" for k, v in (metodo.get("peso_offensivo_per_ruolo") or {}).items()
    )
    # I paragrafi si scrivono per intero e si mandano a capo dopo: cosi' i
    # valori lunghi non spezzano le righe in punti a caso dentro il prompt.
    paragrafi = [
        f"Il TPI (Total Performance Index) e' la media pesata di z-score "
        f"winsorizzati su {len(dims)} dimensioni, calcolate su dati "
        f"Understat/FBref della Serie A:",

        f"{z.get('nota_it', '')} Winsorizzazione al "
        f"{z.get('winsor_pct', 0.05):.0%} prima di standardizzare, poi clamp a "
        f"+/-{z.get('clamp_sigma', 3):.0f} sigma. Peso della fase offensiva per "
        f"ruolo: {pesi_ruolo}. Portieri: {metodo.get('portieri', 'esclusi')}.",

        f"Consistenza: {metodo.get('consistenza_formula', '')}. Forma: EWMA con "
        f"alpha = {metodo.get('ewma_alpha', 0):.2f}.",

        f"Il TPI Pro aggiunge {len(metodo.get('modulatori_pro') or [])} "
        f"modulatori scout, che NON sono dimensioni del TPI base: {pro}. La "
        f"curva d'eta ha il picco a {eta.get('picco', 0):.0f} anni (sigma "
        f"{eta.get('sigma', 0):.1f}): premia chi sta ENTRANDO nel prime, non "
        f"chi ci e' gia' dentro.",

        f"Correzioni statistiche: shrinkage bayesiano sui per-90 verso la media "
        f"di ruolo (K = {shr.get('output_prior_minuti', 0):.0f} minuti, cioe' a "
        f"quei minuti meta' del segnale); SOS, cioe' gli xG concessi reali degli "
        f"avversari affrontati; regressione verso la media di ruolo pesata sulla "
        f"confidence, con pavimento {shr.get('confidence_floor', 0):.2f}; "
        f"penalita disponibilita che non punisce chi e' arrivato a gennaio.",

        f"I {len(metodo.get('contesti') or [])} contesti ({contesti}) sono "
        f"ricalcolati da zero, non filtri sul totale: ogni contesto ha i suoi "
        f"z-score e la sua SOS.",
    ]
    testa = textwrap.fill(paragrafi[0], width=86)
    resto = "\n\n".join(textwrap.fill(p, width=86) for p in paragrafi[1:])
    return f"{testa}\n\n{elenco}\n\n{resto}"


def glossario(metodo: dict) -> dict:
    """Le voci definitorie. Restano a mano perche' sono definizioni, non misure
    — ma quelle che dipendono da una scelta del motore la leggono dal motore."""
    z = metodo.get("z") or {}
    dentro = z.get("dentro_il_ruolo", True)
    zero = ("0 = il giocatore medio del SUO RUOLO" if dentro
            else "0 = il giocatore medio della lega")
    fini = metodo.get("ruoli_specifici") or {}
    elenco = ", ".join(sorted(v.get("nome_it", k).lower() for k, v in fini.items() if k != "POR"))
    return {
        "ruolo_specifico": (f"il ruolo che il giocatore fa davvero, dai minuti per posizione: "
                            f"{elenco}. Non entra nel punteggio: gli z-score restano dentro "
                            f"ATT/CEN/DIF." if elenco else "ruolo specifico"),
        "ruolo_specifico_quota": "quota dei minuti passati in quel ruolo: 0.93 = quasi sempre li'.",
        "contratto_scadenza": ("data di scadenza del contratto (Transfermarkt), formato "
                               "aaaa-mm-gg. NON entra nell'indice."),
        "valore_mercato_eur": ("valore di mercato Transfermarkt in euro. NON entra nell'indice: "
                               "la validazione lo usa come baseline da battere (test Q)."),
        "TPI": f"Total Performance Index, il punteggio complessivo. Piu' alto = meglio. Scala z-score: {zero}.",
        "z": f"z-score winsorizzato a +/-{z.get('clamp_sigma', 3):.0f}. {zero}, +1 = una deviazione standard sopra.",
        "z_pro": "modulatori del TPI Pro (eta, affidabilita fisica). Non sono dimensioni del TPI base.",
        "rank": "posizione in classifica TPI sul totale dei giocatori qualificati.",
        "sos": "Strength of Schedule: >1 = calendario piu' duro della media.",
        "forma": "hot = in crescita, cold = in calo, stable = stabile. Calcolata su media mobile esponenziale delle ultime giornate.",
        "forma_ratio": "output recente diviso output stagionale. >1 = sta rendendo sopra la sua media.",
        "confidence": "0-1, quanto e' affidabile il TPI di quel giocatore (minuti, presenze, stabilita fra contesti, ampiezza dell'intervallo).",
        "affidabilita": "componente del PRI: 1 = sempre disponibile.",
        "eta_cat": "prospetto / prime / veterano.",
    }


def costruisci(src: Path) -> dict:
    payload = json.loads(src.read_text(encoding="utf-8"))
    metodo = payload.get("metodo")
    if not metodo:
        raise SystemExit(
            f"{src.name} non ha il blocco 'metodo': rigeneralo con parte1_analisi.py.\n"
            "Senza quel blocco questo script dovrebbe inventarsi la metodologia, "
            "che e' esattamente il difetto che doveva chiudere."
        )
    players = sorted(
        payload.get("players") or [],
        key=lambda p: (p.get("rank") or {}).get("TPI") or 9999,
    )
    # La stagione la dichiara il payload, come ogni altro campo qui dentro.
    # Era l'unica costante scritta a mano rimasta in un file il cui scopo e'
    # non averne: l'8/9/2026, col sito passato alla 2026-27, il dataset diceva
    # ancora "2025/26" accanto a "n_giornate: 3" — cioe' l'etichetta di un anno
    # e i numeri di un altro, dentro il system prompt di un assistente che
    # risponde con sicurezza.
    stagione_payload = payload.get("stagione")
    if not stagione_payload:
        raise SystemExit(
            f"{src.name} non dichiara la stagione: senza, questo script "
            "dovrebbe scriverla a mano, che e' il difetto da chiudere."
        )
    dataset = {
        "stagione": str(stagione_payload).replace("-", "/"),
        "n_giornate": payload.get("n_giornate"),
        "n_giocatori_analizzati": payload.get("n_giocatori"),
        "top6": payload.get("top6_names"),
        "difese_forti": payload.get("forti_names"),
        "metodologia": metodologia(metodo),
        "glossario": glossario(metodo),
        "giocatori": [compact_player(p) for p in players[:N_PLAYERS]],
    }
    # Le verifiche: se il file c'e' i numeri sono quelli dell'ultima esecuzione,
    # se manca la voce non compare. Meglio muti che approssimativi.
    if VALIDAZIONE.is_file():
        dataset["validazione"] = json.loads(VALIDAZIONE.read_text(encoding="utf-8"))
    return dataset


def serializza(dataset: dict) -> str:
    return json.dumps(dataset, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    argv = [a for a in sys.argv[1:] if a != "--check"]
    check = "--check" in sys.argv
    src = Path(argv[0]) if argv else BASE_DIR / "payload.json"
    if not src.exists():
        print(f"payload non trovato: {src}", file=sys.stderr)
        return 1

    testo = serializza(costruisci(src))

    if check:
        # Il controllo che questo file non resti indietro rispetto al payload:
        # gira in CI e nel pre-commit. Il dataset era vecchio di otto giorni e
        # nessuno se n'era accorto perche' niente lo confrontava con la fonte.
        if not OUT_PATH.exists():
            print(f"{OUT_PATH.name} non esiste: python build_ai_dataset.py", file=sys.stderr)
            return 1
        if OUT_PATH.read_text(encoding="utf-8") != testo:
            print(
                f"{OUT_PATH.name} non corrisponde a {src.name}.\n"
                "Rigeneralo con:  python build_ai_dataset.py",
                file=sys.stderr,
            )
            return 1
        print(f"{OUT_PATH.name}: allineato a {src.name}")
        return 0

    OUT_PATH.write_text(testo, encoding="utf-8")
    kb = OUT_PATH.stat().st_size / 1024
    n = len(json.loads(testo)["giocatori"])
    print(f"{OUT_PATH.name}: {n} giocatori, {kb:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
