"""Riduce payload.json al dataset compatto che l'assistente AI legge.

Il Worker Cloudflare scarica ai_dataset.json e lo mette nel system prompt con
cache_control: quindi conta ogni byte. Qui teniamo solo i campi su cui ha senso
fare domande (ranking, contesti, forma, eta, affidabilita) e buttiamo le serie
per-giornata, che valgono migliaia di token e non servono a una risposta in chat.

Uso:
    python build_ai_dataset.py                 # legge payload.json accanto a questo file
    python build_ai_dataset.py path/al/payload.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "ai_dataset.json"

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
        # z-score delle 6 dimensioni: sono la spiegazione del TPI, non un extra
        "z": {
            "output": r(p.get("z_output")),
            "buildup": r(p.get("z_buildup")),
            "centralita": r(p.get("z_centralita")),
            "boost": r(p.get("z_boost")),
            "consistenza": r(p.get("z_consistenza")),
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


# Sintesi del modello. Non e' documentazione: e' quel che serve all'assistente per
# rispondere "come e' calcolato" senza inventarsi formule. Fonte: guida_completa.html.
METHODOLOGY = """\
Il TPI (Total Performance Index) e' la media pesata di z-score winsorizzati su sei
dimensioni indipendenti, calcolate su dati Understat/FBref della Serie A:

1. Output Adj/90 - npxG + xA per 90', corretti per la forza degli avversari (SOS).
   Usa xG NO-rigori: i rigoristi non vengono premiati per il ruolo.
2. Buildup (xGBuildup) - contributo alle azioni da gol senza tiro/assist finale:
   premia i costruttori di gioco, non solo i finalizzatori.
3. Centralita offensiva - quota di produzione offensiva della squadra che passa
   dal giocatore. Misura quanto la squadra dipende da lui.
4. Team Boost Ratio - xG creati dalla squadra con lui in campo vs senza,
   in log-ratio simmetrico e shrinkato. Nullo se i minuti "senza" sono troppo pochi.
5. Consistenza - stabilita partita su partita basata su IQR (non deviazione standard):
   robusta agli outlier, premia chi rende sempre invece di chi ha 2 partite record.
6. AII (Age Index) - curva gaussiana con picco a 27 anni, orientata a chi ENTRA nel
   prime (22-25 anni) piu' che a chi ci e' gia' dentro.

Il PRI (Physical Reliability Index) pesa disponibilita, infortuni e gravita; entra nel
TPI Pro insieme ad AII.

Correzioni statistiche applicate:
- Bayesian shrinkage dinamico sui per-90: chi ha pochi minuti viene tirato verso la
  media di ruolo, quindi i subentranti non scalano la classifica con 200 minuti.
- SOS (Strength of Schedule): xG concessi reali degli avversari affrontati.
- Winsorized z-score a +/-3 sigma.
- Penalita disponibilita consapevole del mercato invernale: chi arriva a gennaio non
  viene punito per le giornate in cui non era in rosa.
- Confidence score a 4 fattori (minuti, presenze, stabilita fra contesti, ampiezza CI).

Validazione (validazione.html): Spearman rho = 0.70 nel backtest predittivo
prima meta -> seconda meta di stagione, bootstrap CI 95%, Kendall tau per la
stabilita del ranking, overlap top-10 contro WhoScored.

I 5 contesti (totale, casa, trasferta, vs top 6, vs difese forti) sono ricalcolati
da zero, non filtri sul totale: ogni contesto ha i suoi z-score e la sua SOS.\
"""

GLOSSARY = {
    "TPI": "Total Performance Index, il punteggio complessivo. Piu' alto = meglio. Scala z-score, quindi 0 = giocatore medio della Serie A analizzata.",
    "z": "z-score winsorizzato a +/-3. 0 = media, +1 = una deviazione standard sopra la media.",
    "rank": "posizione in classifica TPI sul totale dei giocatori analizzati.",
    "sos": "Strength of Schedule: >1 = calendario piu' duro della media.",
    "forma": "hot = in crescita, cold = in calo, stable = stabile. Calcolata su EWMA delle ultime giornate.",
    "forma_ratio": "output recente diviso output stagionale. >1 = sta rendendo sopra la sua media.",
    "confidence": "0-1, quanto e' affidabile il TPI di quel giocatore (minuti, presenze, stabilita).",
    "affidabilita": "componente del PRI: 1 = sempre disponibile.",
    "eta_cat": "young / prime / veteran.",
}


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR / "payload.json"
    if not src.exists():
        print(f"payload non trovato: {src}", file=sys.stderr)
        return 1

    payload = json.loads(src.read_text(encoding="utf-8"))
    players = payload.get("players") or []
    players = sorted(players, key=lambda p: (p.get("rank") or {}).get("TPI") or 9999)

    dataset = {
        "stagione": "2025/26",
        "n_giornate": payload.get("n_giornate"),
        "n_giocatori_analizzati": payload.get("n_giocatori"),
        "top6": payload.get("top6_names"),
        "difese_forti": payload.get("forti_names"),
        "metodologia": METHODOLOGY,
        "glossario": GLOSSARY,
        "giocatori": [compact_player(p) for p in players[:N_PLAYERS]],
    }

    OUT_PATH.write_text(
        json.dumps(dataset, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    kb = OUT_PATH.stat().st_size / 1024
    print(f"{OUT_PATH.name}: {len(dataset['giocatori'])} giocatori, {kb:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
