"""Il dataset dell'assistente e' allineato al payload pubblicato?

Committarlo vecchio non rompe niente in modo visibile: l'assistente continua a
rispondere, solo con i numeri di prima. E' successo — il file e' rimasto
indietro di otto giorni con dentro una metodologia che il motore non usava piu'.
Per questo il controllo esiste, e gira sia nel pre-commit che in CI.

DUE CONTROLLI, PERCHE' I DUE POSTI SANNO COSE DIVERSE
----------------------------------------------------
Il generatore, `build_ai_dataset.py`, sta nel motore: questo repo pubblica il
sito, e un generatore non e' il sito.

* **Sul computer di chi lavora** il motore e' nella cartella accanto. Allora si
  chiama lui: rigenera il dataset in memoria e lo confronta byte per byte. E'
  il controllo forte, e non c'e' ragione di accontentarsi di meno.
* **In CI** il motore non c'e' — questo repo si clona da solo. Li' si guarda
  quello che il dataset dichiara di se' e lo si confronta col payload che gli
  sta accanto: stagione, giornate, quanti giocatori, e i primi cento nell'ordine
  in cui il payload li mette. Non prova che ogni campo sia aggiornato, ma prende
  tutto quello che e' andato storto davvero: un file rimasto a un'altra
  stagione, o a un'altra giornata, o a un'altra classifica.

La prima versione, in CI, saltava e basta. Dopo lo spostamento del generatore
l'8/9/2026 il workflow ha cominciato a fallire a ogni push — cercava un file che
non c'e' piu' in questo repo — e un controllo rosso a ogni commit e' un
controllo che si impara a ignorare.
"""
import json
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
MOTORE = QUI.parent / "serie-a-index-engine" / "build_ai_dataset.py"
QUANTI = 100          # i giocatori che il dataset porta, i primi per rank TPI


def col_motore() -> int:
    return subprocess.run(
        [sys.executable, str(MOTORE), "--check", str(QUI / "payload.json")],
        cwd=str(MOTORE.parent),
    ).returncode


def da_solo() -> int:
    """Confronta quello che il dataset dichiara col payload che gli sta accanto."""
    try:
        pay = json.loads((QUI / "payload.json").read_text(encoding="utf-8"))
        ai = json.loads((QUI / "ai_dataset.json").read_text(encoding="utf-8"))
    except OSError as e:
        print("manca un file: %s" % e, file=sys.stderr)
        return 1
    except ValueError as e:
        print("un file non e' JSON valido: %s" % e, file=sys.stderr)
        return 1

    guai = []
    attesa = str(pay.get("stagione") or "").replace("-", "/")
    if ai.get("stagione") != attesa:
        guai.append("stagione: il dataset dice %r, il payload %r"
                    % (ai.get("stagione"), attesa))
    for campo_ai, campo_pay in (("n_giornate", "n_giornate"),
                                ("n_giocatori_analizzati", "n_giocatori")):
        if ai.get(campo_ai) != pay.get(campo_pay):
            guai.append("%s: il dataset dice %r, il payload %r"
                        % (campo_ai, ai.get(campo_ai), pay.get(campo_pay)))

    # L'ordine, che e' la cosa che cambia a ogni giornata: il dataset porta i
    # primi cento per rank TPI, e devono essere quelli, in quell'ordine.
    attesi = [g.get("nome") for g in sorted(
        pay.get("players") or [],
        key=lambda g: (g.get("rank") or {}).get("TPI") or 10**9)][:QUANTI]
    dentro = [g.get("nome") for g in (ai.get("giocatori") or [])]
    if dentro != attesi:
        diversi = [(a, b) for a, b in zip(dentro, attesi) if a != b]
        guai.append("i primi %d non coincidono (%d posizioni diverse; prima: "
                    "il dataset ha %r dove il payload ha %r)"
                    % (QUANTI, len(diversi) or abs(len(dentro) - len(attesi)),
                       diversi[0][0] if diversi else None,
                       diversi[0][1] if diversi else None))

    if guai:
        print("ai_dataset.json non corrisponde a payload.json:", file=sys.stderr)
        for g in guai:
            print("  - %s" % g, file=sys.stderr)
        print("\nRigeneralo dal motore:  python build_ai_dataset.py", file=sys.stderr)
        return 1
    print("ai_dataset.json: allineato a payload.json "
          "(stagione, giornate, qualificati e i primi %d)" % QUANTI)
    return 0


def main() -> int:
    return col_motore() if MOTORE.is_file() else da_solo()


if __name__ == "__main__":
    raise SystemExit(main())
