"""A Teia da Byte: transforma o gráfico de contribuições do último ano numa teia.

Cada dia com contribuição vira uma gota de orvalho presa na teia. A Byte percorre
as contribuições em ordem cronológica, puxando um fio de seda até cada uma, e as
gotas acendem quando ela passa.

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

W, H = 880, 236
X0, Y0, DX, DY = 44, 74, 15.4, 16.0
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
DROP = ["#13213d", "#2f5fb3", "#3a86ff", "#7fb8ff", "#00d4ff"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

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


def pos(wi, wd):
    return X0 + wi * DX, Y0 + wd * DY


def f(v):
    return f"{v:.1f}"


def corner_web(cx, cy, r, a0, a1, n=6, rings=4):
    """Teia em leque presa num canto."""
    spokes, arcs = [], []
    angs = [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]
    for a in angs:
        spokes.append(f"M{f(cx)} {f(cy)} L{f(cx + r * math.cos(a))} {f(cy + r * math.sin(a))}")
    for k in range(1, rings + 1):
        rr = r * k / (rings + .4)
        p = [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for a in angs]
        d = f"M{f(p[0][0])} {f(p[0][1])}"
        for (x1, y1), (x2, y2) in zip(p, p[1:]):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            d += f" Q{f(mx + (cx - mx) * .12)} {f(my + (cy - my) * .12)} {f(x2)} {f(y2)}"
        arcs.append(d)
    return " ".join(spokes + arcs)


def build(total, weeks, user):
    nodes = []  # (x, y, level, date)
    for wi, week in enumerate(weeks):
        for d in week:
            x, y = pos(wi, d["weekday"])
            nodes.append((x, y, LEVEL.get(d["contributionLevel"], 0) if d["contributionCount"] else 0, d["date"]))
    hits = [n for n in nodes if n[2] > 0]

    # --- a teia: fios entre nós vizinhos, levemente curvados ---
    grid = {}
    for wi, week in enumerate(weeks):
        for d in week:
            grid[(wi, d["weekday"])] = pos(wi, d["weekday"])
    silk = []
    for (wi, wd), (x, y) in grid.items():
        if (wi + 1, wd) in grid:
            x2, y2 = grid[(wi + 1, wd)]
            silk.append(f"M{f(x)} {f(y)} Q{f((x + x2) / 2)} {f(y + 1.6)} {f(x2)} {f(y2)}")
        if (wi, wd + 1) in grid and wi % 2 == 0:
            x2, y2 = grid[(wi, wd + 1)]
            silk.append(f"M{f(x)} {f(y)} Q{f(x - 1.2)} {f((y + y2) / 2)} {f(x2)} {f(y2)}")
    # fios de ancoragem nas bordas
    anchors = []
    for wd in range(7):
        x, y = pos(0, wd)
        anchors.append(f"M16 {f(y - 6 + wd * 2)} L{f(x)} {f(y)}")
        x, y = pos(len(weeks) - 1, wd)
        if (len(weeks) - 1, wd) in grid:
            anchors.append(f"M{W - 16} {f(y - 6 + wd * 2)} L{f(x)} {f(y)}")

    # --- rótulos de meses ---
    labels, last = [], None
    for wi, week in enumerate(weeks):
        m = int(week[0]["date"][5:7])
        if m != last and wi < len(weeks) - 2:
            labels.append(f'<text x="{f(X0 + wi * DX - 4)}" y="{f(Y0 - 14)}" class="m">{MESES[m - 1]}</text>')
        last = m

    # --- caminho da Byte: entra pela esquerda e visita cada contribuição ---
    start = (X0 - 30, Y0 + 3 * DY)
    pts = [start] + [(x, y) for x, y, _, _ in hits]
    if len(pts) == 1:
        pts.append((W / 2, Y0 + 3 * DY))
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(segs) or 1
    path = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts)

    TRAVEL = 0.82                              # fração do ciclo em que ela anda
    D = max(10.0, min(28.0, 3.0 + L / 70))    # duração do ciclo em segundos
    acc, arrive = 0.0, []
    for s in segs:
        acc += s
        arrive.append(acc / L * TRAVEL)

    drops = []
    for (x, y, lv, date), t in zip(hits, arrive):
        t = min(max(t, 0.001), 0.95)
        c = DROP[lv]
        kt = f"0;{t:.4f};{min(t + .02, .96):.4f};0.96;1"
        drops.append(f'''
      <g>
        <circle cx="{f(x)}" cy="{f(y)}" r="{3.2 + lv * .55:.2f}" fill="{c}" opacity=".18">
          <animate attributeName="opacity" dur="{D:.1f}s" repeatCount="indefinite" keyTimes="{kt}" values=".18;.18;1;1;.18"/>
        </circle>
        <circle cx="{f(x)}" cy="{f(y)}" r="9" fill="{c}" opacity="0" filter="url(#tglow)">
          <animate attributeName="opacity" dur="{D:.1f}s" repeatCount="indefinite" keyTimes="{kt}" values="0;0;.55;.25;0"/>
        </circle>
        <title>{date}</title>
      </g>''')

    dots = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="1.5" fill="#1e3a6e"/>' for x, y, lv, _ in nodes if lv == 0)

    byte = sp.spider("tb", 2)
    hit_txt = f"{total} contribuiç{'ão' if total == 1 else 'ões'} no último ano" if total else "A teia está esperando o primeiro fio"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    {sp.defs("tb")}
    <filter id="tglow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3"/></filter>
    <linearGradient id="thread" x1="0" x2="1"><stop offset="0" stop-color="#7fb8ff"/><stop offset="1" stop-color="#cfe2ff"/></linearGradient>
    <style>
      .t {{ font-family:'Segoe UI', Ubuntu, sans-serif }}
      .h {{ font-weight:600; font-size:18px; fill:#00D4FF }}
      .s {{ font-size:12px; fill:#7f9cc9 }}
      .m {{ font-family:'Segoe UI', Ubuntu, sans-serif; font-size:10px; fill:#5f7ba6 }}
{sp.CSS}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="6" fill="#060A14"/>
  <text x="24" y="32" class="t h">A Teia da Byte</text>
  <text x="{W - 84}" y="32" class="t s" text-anchor="end">{hit_txt}</text>
  {"".join(labels)}

  <!-- teias de canto -->
  <g fill="none" stroke="#7fb8ff" stroke-opacity=".16" stroke-width=".9">
    <path d="{corner_web(W - 6, 6, 70, math.pi / 2, math.pi)}"/>
    <path d="{corner_web(6, H - 6, 60, -math.pi / 2, 0)}"/>
  </g>

  <!-- teia -->
  <g fill="none" stroke="#3a86ff" stroke-opacity=".13" stroke-width=".8">
    <path d="{" ".join(silk)}"/>
    <path d="{" ".join(anchors)}" stroke-opacity=".18"/>
  </g>
  {dots}

  <!-- fio que a Byte puxa -->
  <path d="{path}" fill="none" stroke="url(#thread)" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"
        pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000" opacity=".85">
    <animate attributeName="stroke-dashoffset" dur="{D:.1f}s" repeatCount="indefinite" calcMode="linear"
             keyTimes="0;{TRAVEL};0.96;1" values="1000;0;0;1000"/>
    <animate attributeName="opacity" dur="{D:.1f}s" repeatCount="indefinite" keyTimes="0;0.9;0.97;1" values=".85;.85;0;0"/>
  </path>

  <!-- gotas de orvalho (contribuições) -->
  {"".join(drops)}

  <!-- Byte -->
  <g>
    <animateMotion dur="{D:.1f}s" repeatCount="indefinite" calcMode="linear" path="{path}"
                   keyPoints="0;1;1" keyTimes="0;{TRAVEL};1"/>
    <g transform="translate(0,-10) scale(.26)">{byte}</g>
  </g>

  <text x="64" y="{H - 16}" class="t s">Cada contribuição vira uma gota na teia, e a Byte tece um fio até cada uma.</text>
  <g transform="translate({W - 170},{H - 20})" class="t">
    <text class="s" x="0" y="4">menos</text>
    {"".join(f'<circle cx="{46 + i * 16}" cy="0" r="{3.2 + i * .55:.1f}" fill="{c}"/>' for i, c in enumerate(DROP))}
    <text class="s" x="{46 + 5 * 16}" y="4">mais</text>
  </g>
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
