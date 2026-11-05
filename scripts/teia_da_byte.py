"""A Teia da Byte: transforma o último ano de contribuições numa teia circular.

Cada raio marca o início de um mês e cada anel é um dia da semana (domingo no
centro, sábado na borda). Cada dia com contribuição vira uma gota de orvalho.
A Byte fica no centro e, de tempos em tempos, puxa a teia: uma onda de vibração
sai do centro e acende as gotas por onde passa, enquanto a teia balança ao vento.

Uso:
  GITHUB_TOKEN=... python3 scripts/teia_da_byte.py --user FelipeAUGraciano --out dist/teia-da-byte.svg
  python3 scripts/teia_da_byte.py --demo --out teia.svg     # dados de exemplo, sem rede
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import byte_spider as sp  # noqa: E402

W, H = 880, 324
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
DROP = ["#13213d", "#2f5fb3", "#3a86ff", "#7fb8ff", "#00d4ff"]

QUERY = """query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
  totalContributions weeks{ contributionDays{ date contributionCount contributionLevel weekday } } } } } }"""


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "teia-da-byte"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"Erro da API do GitHub: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [w["contributionDays"] for w in cal["weeks"]]


def demo():
    random.seed(4)
    end = dt.date(2026, 11, 5)
    start = end - dt.timedelta(days=end.weekday() + 1 + 52 * 7)
    weeks, day, total = [], start, 0
    picks = {12, 14, 26, 46, 48, 49, 50, 52}
    while day <= end:
        week = []
        for _ in range(7):
            if day > end:
                break
            w = len(weeks)
            n = random.choice([1, 1, 2, 3]) if (w in picks and random.random() < .35) else 0
            total += n
            lv = "NONE" if n == 0 else ("FIRST_QUARTILE" if n == 1 else "SECOND_QUARTILE" if n == 2 else "FOURTH_QUARTILE")
            week.append({"date": day.isoformat(), "contributionCount": n, "contributionLevel": lv, "weekday": (day.weekday() + 1) % 7})
            day += dt.timedelta(days=1)
        weeks.append(week)
    return total, weeks


def f(v):
    return f"{v:.1f}"


CX, CY = 250, 162          # centro da teia
R0, DR = 46, 13            # raio do primeiro anel e distância entre anéis (7 anéis = dias da semana)
WAVE = 4.0                 # período da onda de vibração (s)


def polar(a, r):
    return CX + r * math.cos(a), CY + r * math.sin(a)


def build(total, weeks, user):
    days = [d for w in weeks for d in w]
    n = len(days) or 1
    ang = lambda i: -math.pi / 2 + 2 * math.pi * i / n

    # raios: início de cada mês + um raio intermediário no meio do mês
    month_start = [i for i, d in enumerate(days)
                   if i > 0 and d["date"][5:7] != days[i - 1]["date"][5:7] and n - i >= 10]
    if not month_start or month_start[0] > 10:
        month_start = [0] + month_start
    spoke_idx = []
    for k, i in enumerate(month_start):
        nxt = month_start[k + 1] if k + 1 < len(month_start) else n + month_start[0]
        spoke_idx += [i, (i + nxt) / 2]
    spokes = sorted(set(ang(i) % (2 * math.pi) for i in spoke_idx))
    rmax = R0 + 6 * DR

    web = []
    for a in spokes:
        x1, y1 = polar(a, 18); x2, y2 = polar(a, rmax + 10)
        web.append(f"M{f(x1)} {f(y1)} L{f(x2)} {f(y2)}")
    for k in range(7):
        r = R0 + k * DR
        for a1, a2 in zip(spokes, spokes[1:] + [spokes[0] + 2 * math.pi]):
            x1, y1 = polar(a1, r); x2, y2 = polar(a2, r)
            cx, cy = polar((a1 + a2) / 2, r * .9)      # fio cede um pouco para dentro
            web.append(f"M{f(x1)} {f(y1)} Q{f(cx)} {f(cy)} {f(x2)} {f(y2)}")
    # fios do miolo (espiral de captura do centro)
    hub = []
    for k in range(3):
        r = 20 + k * 8
        pts = [polar(a, r) for a in spokes]
        hub.append("M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + " Z")
    # fios de ancoragem até as bordas
    anchors = []
    for a, (ex, ey) in [(-2.4, (0, 0)), (-0.7, (CX + 230, 0)), (0.75, (CX + 210, H)), (2.3, (0, H)), (3.14, (0, CY - 10))]:
        x, y = polar(a, rmax + 10)
        anchors.append(f"M{f(x)} {f(y)} L{ex} {ey}")

    # rótulos dos meses
    MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    labels = []
    for k, i in enumerate(month_start):
        nxt = month_start[k + 1] if k + 1 < len(month_start) else n + month_start[0]
        x, y = polar(ang((i + nxt) / 2), rmax + 22)
        labels.append(f'<text x="{f(x)}" y="{f(y + 3.5)}" class="m" text-anchor="middle">{MES[int(days[i]["date"][5:7]) - 1]}</text>')

    # gotas de orvalho
    drops, active = [], []
    for i, d in enumerate(days):
        if not d["contributionCount"]:
            continue
        lv = LEVEL.get(d["contributionLevel"], 1) or 1
        a = ang(i)
        # posição sobre o fio cedido entre dois raios
        a_mod = a % (2 * math.pi)
        prev = max([s for s in spokes if s <= a_mod] or [spokes[-1] - 2 * math.pi])
        nxts = [s for s in spokes if s > a_mod] or [spokes[0] + 2 * math.pi]
        frac = (a_mod - prev) / ((nxts[0] - prev) or 1)
        r = (R0 + d["weekday"] * DR) * (1 - .1 * math.sin(math.pi * frac) ** 2 * .9)
        x, y = polar(a, r)
        active.append(d)
        rad = 2.6 + lv * .7
        c = DROP[lv]
        t0 = (r - 22) / (rmax + 10 - 22) * WAVE * .55        # quando a onda passa por aqui
        tw = (i * .37) % 3
        drops.append(f'''
    <g>
      <circle cx="{f(x)}" cy="{f(y)}" r="{rad + 5:.1f}" fill="{c}" opacity="0" filter="url(#tglow)">
        <animate attributeName="opacity" dur="{WAVE}s" begin="{t0:.2f}s" repeatCount="indefinite" values="0;.85;0" keyTimes="0;.12;.5"/>
      </circle>
      <circle cx="{f(x)}" cy="{f(y)}" r="{rad:.1f}" fill="url(#drop{lv})">
        <animate attributeName="opacity" dur="3s" begin="{tw:.2f}s" repeatCount="indefinite" values=".75;1;.75"/>
      </circle>
      <circle cx="{f(x - rad * .35)}" cy="{f(y - rad * .35)}" r="{rad * .3:.1f}" fill="#fff" opacity=".85"/>
      <title>{d["date"]}: {d["contributionCount"]} contribuiç{"ão" if d["contributionCount"] == 1 else "ões"}</title>
    </g>''')

    # números para o painel
    by_month = {}
    for d in active:
        by_month[d["date"][:7]] = by_month.get(d["date"][:7], 0) + d["contributionCount"]
    best_m = max(by_month, key=by_month.get) if by_month else None
    best_d = max(active, key=lambda d: d["contributionCount"]) if active else None
    def br(date):
        return f"{date[8:10]}/{date[5:7]}"
    lines = [
        (f"{total}", f"contribuiç{'ão' if total == 1 else 'ões'} no último ano"),
        (f"{len(active)}", f"dia{'s' if len(active) != 1 else ''} tecido{'s' if len(active) != 1 else ''} na teia"),
    ]
    if best_m:
        lines.append((MES[int(best_m[5:7]) - 1].capitalize(), "mês mais ativo"))
    if best_d:
        lines.append((br(best_d["date"]), f"maior gota ({best_d['contributionCount']} contribuiç{'ão' if best_d['contributionCount'] == 1 else 'ões'})"))
    panel = "".join(
        f'<g transform="translate(540,{124 + k * 36})"><text class="big">{v}</text><text x="{16 + len(v) * 13}" y="-1" class="s">{t}</text></g>'
        for k, (v, t) in enumerate(lines))

    byte = sp.spider("tb", 2)
    spline = 'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" keyTimes="0;.5;1"'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    {sp.defs("tb")}
    <filter id="tglow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3.2"/></filter>
    <radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#3a86ff" stop-opacity=".18"/><stop offset="1" stop-color="#3a86ff" stop-opacity="0"/></radialGradient>
    {"".join(f'<radialGradient id="drop{k}" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="{DROP[k]}"/><stop offset="1" stop-color="{DROP[max(k - 1, 1)]}"/></radialGradient>' for k in range(1, 5))}
    <clipPath id="card"><rect width="{W}" height="{H}" rx="6"/></clipPath>
    <style>
      .t {{ font-family:'Segoe UI', Ubuntu, sans-serif }}
      .h {{ font-family:'Segoe UI', Ubuntu, sans-serif; font-weight:600; font-size:22px; fill:#00D4FF }}
      .big {{ font-family:'Segoe UI', Ubuntu, sans-serif; font-weight:700; font-size:22px; fill:#EEF5FF }}
      .s {{ font-family:'Segoe UI', Ubuntu, sans-serif; font-size:13px; fill:#7f9cc9 }}
      .m {{ font-family:'Segoe UI', Ubuntu, sans-serif; font-size:10px; fill:#5f7ba6 }}
{sp.CSS}
    </style>
  </defs>
  <g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="#060A14"/>
  <circle cx="{CX}" cy="{CY}" r="{rmax + 30}" fill="url(#halo)"/>

  <!-- teia (balança devagar com o vento) -->
  <g>
    <animateTransform attributeName="transform" type="rotate" dur="9s" repeatCount="indefinite" {spline}
      values="-1.4 {CX} {CY};1.4 {CX} {CY};-1.4 {CX} {CY}"/>
    <g fill="none" stroke-linecap="round">
      <path d="{" ".join(anchors)}" stroke="#7fb8ff" stroke-opacity=".22" stroke-width="1"/>
      <path d="{" ".join(web)}" stroke="#7fb8ff" stroke-opacity=".2" stroke-width=".9"/>
      <path d="{" ".join(hub)}" stroke="#7fb8ff" stroke-opacity=".3" stroke-width=".9"/>
    </g>
    {"".join(labels)}

    <!-- onda de vibração saindo do centro -->
    <circle cx="{CX}" cy="{CY}" r="22" fill="none" stroke="#7fb8ff" stroke-width="2" opacity="0">
      <animate attributeName="r" dur="{WAVE}s" repeatCount="indefinite" values="22;{rmax + 14}" keyTimes="0;.55" calcMode="spline" keySplines=".2 .6 .4 1"/>
      <animate attributeName="opacity" dur="{WAVE}s" repeatCount="indefinite" values=".55;0;0" keyTimes="0;.55;1"/>
      <animate attributeName="stroke-width" dur="{WAVE}s" repeatCount="indefinite" values="3;.5;.5" keyTimes="0;.55;1"/>
    </circle>

    <!-- gotas de orvalho = contribuições -->
    {"".join(drops)}

    <!-- Byte no centro da teia, dando um puxão a cada onda -->
    <g transform="translate({CX},{CY + 4})">
      <g>
        <animateTransform attributeName="transform" type="translate" dur="{WAVE}s" repeatCount="indefinite"
          values="0 0;0 3;0 0;0 0" keyTimes="0;.06;.2;1" calcMode="spline" keySplines=".3 0 .7 1;.3 0 .7 1;0 0 1 1"/>
        <g transform="scale(.3)">{byte}</g>
      </g>
    </g>
  </g>

  <!-- painel -->
  <text x="540" y="70" class="h">A Teia da Byte</text>
  <text x="540" y="92" class="s">O seu último ano de contribuições, tecido em seda.</text>
  {panel}
  <g transform="translate(540,284)">
    <text class="s" y="4">menos</text>
    {"".join(f'<circle cx="{52 + k * 18}" cy="0" r="{2.6 + k * .7:.1f}" fill="url(#drop{k})"/>' for k in range(1, 5))}
    <text class="s" x="{52 + 4 * 18 + 14}" y="4">mais</text>
  </g>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="none" stroke="#1e3a6e"/>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", ""))
    ap.add_argument("--out", default="dist/teia-da-byte.svg")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        total, weeks = demo()
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token or not a.user:
            raise SystemExit("Defina GITHUB_TOKEN e --user (ou use --demo).")
        total, weeks = fetch(a.user, token)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(build(total, weeks, a.user))
    print(f"Teia gerada em {a.out} ({total} contribuições)")


if __name__ == "__main__":
    main()
