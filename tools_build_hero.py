"""Genera il blocco classifica dell'apertura leggendo payload.json.

I dati finiscono inlinati nell'HTML invece che caricati a runtime: payload.json
non e' pubblicato su Pages, quindi una fetch darebbe 404. Rigenerare con questo
script quando il payload cambia.
"""
import json
import pathlib

DIM = {
    "output_adj": ("output", "Output"),
    "centralita": ("centralità", "Centrality"),
    "boost": ("boost", "Boost"),
    "consistenza": ("consistenza", "Consistency"),
    "conv": ("G/xG", "G/xG"),
}
ROLE = {"ATT": "clay", "CEN": "green", "DIF": "blue", "POR": "lt"}
N = 8

d = json.loads(pathlib.Path("payload.json").read_text(encoding="utf-8"))
players = sorted(d["players"], key=lambda p: -p["tpi"]["totale"])[:N]
top = players[0]["tpi"]["totale"]

rows = []
for i, p in enumerate(players, 1):
    r = p.get("rank", {})
    # Le due dimensioni in cui il giocatore sta piu' in alto: dicono *perche'*
    # e' li', cosa che il solo totale non dice.
    best = sorted(
        ((k, v) for k, v in r.items() if k in DIM and isinstance(v, int)),
        key=lambda kv: kv[1],
    )[:2]
    it = " · ".join("#%d %s" % (v, DIM[k][0]) for k, v in best)
    en = " · ".join("#%d %s" % (v, DIM[k][1]) for k, v in best)
    rows.append(
        '        <a class="lb-row" href="dashboard_serie_a.html">\n'
        '          <span class="lb-n">%02d</span>\n'
        '          <span class="lb-id">\n'
        '            <span class="lb-nm">%s</span>\n'
        '            <span class="lb-why" data-it="%s" data-en="%s">%s</span>\n'
        '          </span>\n'
        '          <span class="lb-tm">%s</span>\n'
        '          <span class="lb-bar"><span style="width:%.1f%%;background:var(--%s)"></span></span>\n'
        '          <span class="lb-v">+%.2f</span>\n'
        '        </a>'
        % (i, p["nome"], it, en, it, p["squadra"],
           p["tpi"]["totale"] / top * 100, ROLE.get(p["ruolo"], "lt"),
           p["tpi"]["totale"])
    )

rest = d["n_giocatori"] - N
block = "\n".join(rows)
pathlib.Path("hero_rows.html").write_text(block, encoding="utf-8")
print("righe generate: %d · altri %d giocatori · n_giornate %d"
      % (len(rows), rest, d["n_giornate"]))
