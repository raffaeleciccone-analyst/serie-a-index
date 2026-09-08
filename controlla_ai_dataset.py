"""Il dataset dell'assistente e' allineato al payload pubblicato?

Il controllo vero lo fa `build_ai_dataset.py --check`, che sta nel motore: qui
c'e' solo il modo di chiamarlo dal gancio del pre-commit di questo repo, che
pubblica il sito e non contiene generatori.

Perche' esiste. L'8/9/2026 il commit del cambio stagione si e' fermato proprio
qui: `ai_dataset.json` era rimasto all'annata prima. Il gancio ha fatto il suo
lavoro, e rigenerando il file e' venuto fuori un difetto peggiore — la stagione
era l'unica costante scritta a mano in quel dataset, che diceva "2025/26"
accanto ai numeri della 2026/27, dentro il prompt di un assistente che risponde
con sicurezza. Adesso il dataset lo riscrive la sequenza di pubblicazione, ma il
gancio resta: e' la seconda rete, e la prima volta ha pagato.

Se il motore non e' accanto a questo repo il controllo non fallisce, si salta e
lo dice. Chi clona solo il sito non ha niente da controllare, e un gancio che si
rompe per una cartella mancante e' un gancio che si disattiva.
"""
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
MOTORE = QUI.parent / "serie-a-index-engine" / "build_ai_dataset.py"


def main() -> int:
    if not MOTORE.is_file():
        print(f"motore non trovato in {MOTORE.parent}: controllo saltato")
        return 0
    return subprocess.run(
        [sys.executable, str(MOTORE), "--check", str(QUI / "payload.json")],
        cwd=str(MOTORE.parent),
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
