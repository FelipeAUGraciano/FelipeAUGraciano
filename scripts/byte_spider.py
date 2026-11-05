"""Byte, versão Cavaleira de Seda (baseada na folha de conceito do usuário).
Vista frontal, centro (0,0), patas tocando o chão em y≈70."""
import math

OUT = "#07061f"   # contorno
INDIGO = "#1c1b63"
GOLD = "#c98a1c"


def defs(p):
    return f'''
    <radialGradient id="{p}abd" cx="0.36" cy="0.3" r="0.8">
      <stop offset="0" stop-color="#4146b8"/><stop offset="0.5" stop-color="#22217a"/><stop offset="1" stop-color="#0d0c38"/>
    </radialGradient>
    <radialGradient id="{p}head" cx="0.4" cy="0.25" r="0.85">
      <stop offset="0" stop-color="#3a3ca6"/><stop offset="0.65" stop-color="#1f1e6b"/><stop offset="1" stop-color="#0f0e3d"/>
    </radialGradient>
    <linearGradient id="{p}leg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2e2d86"/><stop offset="1" stop-color="#14134a"/>
    </linearGradient>
    <linearGradient id="{p}moon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#eef0ff"/><stop offset="0.45" stop-color="#a9b0ec"/><stop offset="0.75" stop-color="#c9b9ff"/><stop offset="1" stop-color="#7a82d0"/>
    </linearGradient>
    <linearGradient id="{p}silk" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#c9d6ff"/><stop offset="0.5" stop-color="#9fb4f0"/><stop offset="1" stop-color="#6f86d8"/>
    </linearGradient>
    <linearGradient id="{p}crysL" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e2f6ff"/><stop offset="1" stop-color="#7cc8ff"/>
    </linearGradient>
    <linearGradient id="{p}crysR" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7cc8ff"/><stop offset="1" stop-color="#2f6fe0"/>
    </linearGradient>
    <radialGradient id="{p}eye" cx="0.42" cy="0.38" r="0.7">
      <stop offset="0" stop-color="#ffd877"/><stop offset="0.55" stop-color="#f5a623"/><stop offset="1" stop-color="#b8640a"/>
    </radialGradient>
    <radialGradient id="{p}runeglow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#5fb8ff" stop-opacity=".55"/><stop offset="1" stop-color="#5fb8ff" stop-opacity="0"/>
    </radialGradient>
    <filter id="{p}glow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="1.8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
'''


CSS = '''
      .byte-breath { animation: bytebreath 2.6s ease-in-out infinite }
      @keyframes bytebreath { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
      .byte-eyes { transform-box:fill-box; transform-origin:50% 50%; animation: byteblink 4.5s infinite }
      @keyframes byteblink { 0%,93%,100%{transform:scaleY(1)} 96%{transform:scaleY(.1)} }
      .byte-rune { animation: byterune 2.4s ease-in-out infinite }
      @keyframes byterune { 0%,100%{opacity:.7} 50%{opacity:1} }
      .byte-mini { animation: bytemini 1.8s ease-in-out infinite }
      .byte-mini.m2{animation-delay:.3s} .byte-mini.m3{animation-delay:.6s}
      @keyframes bytemini { 0%,100%{opacity:.65} 50%{opacity:1} }
      .byte-blade { animation: byteglint 2s ease-in-out infinite }
      @keyframes byteglint { 0%,100%{filter:brightness(1)} 50%{filter:brightness(1.35)} }
'''


def _f(p):
    return f"{p[0]:.1f} {p[1]:.1f}"


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _norm(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return (-dy / L, dx / L), (dx / L, dy / L), L


def _plate(c, along, size, P):
    """Placa de pedra-da-lua facetada orientada ao longo de 'along'."""
    (nx, ny), (ux, uy), _ = _norm((0, 0), along)
    s = size
    pts = [(c[0] + ux * s * 1.3, c[1] + uy * s * 1.3),
           (c[0] + nx * s * .9 + ux * s * .2, c[1] + ny * s * .9 + uy * s * .2),
           (c[0] - ux * s * 1.1, c[1] - uy * s * 1.1),
           (c[0] - nx * s * .7 - ux * s * .1, c[1] - ny * s * .7 - uy * s * .1)]
    poly = " ".join(_f(p) for p in pts)
    return (f'<polygon points="{poly}" fill="url(#{P}moon)" stroke="#4a4f9e" stroke-width="1.4" stroke-linejoin="round"/>'
            f'<path d="M{_f(pts[0])} L{_f(c)} L{_f(pts[2])}" stroke="#ffffff" stroke-width=".9" opacity=".7" fill="none"/>')


def _leg(hip, knee, foot, P, blade):
    ankle = _lerp(knee, foot, 0.62 if blade else 0.7)
    out = f'''
      <g>
        <path d="M{_f(hip)} L{_f(knee)} L{_f(ankle)}" stroke="{OUT}" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M{_f(hip)} L{_f(knee)}" stroke="url(#{P}leg)" stroke-width="8.5" fill="none" stroke-linecap="round"/>
        <path d="M{_f(knee)} L{_f(ankle)}" stroke="url(#{P}leg)" stroke-width="6.5" fill="none" stroke-linecap="round"/>'''
    # brilho de borda
    (nx, ny), _, _ = _norm(hip, knee)
    if ny > 0:
        nx, ny = -nx, -ny
    out += f'''
        <path d="M{hip[0]+nx*2.4:.1f} {hip[1]+ny*2.4:.1f} L{knee[0]+nx*2.4:.1f} {knee[1]+ny*2.4:.1f}" stroke="#5a60d6" stroke-width="1.8" stroke-linecap="round" opacity=".9"/>'''
    out += _plate(_lerp(hip, knee, .55), (knee[0] - hip[0], knee[1] - hip[1]), 5.2, P)
    if blade:
        (bx, by), (ux, uy), L = _norm(ankle, foot)
        w = 6.5
        mid = _lerp(ankle, foot, .35)
        left = (mid[0] + bx * w, mid[1] + by * w)
        right = (mid[0] - bx * w, mid[1] - by * w)
        tip = (foot[0] + ux * 6, foot[1] + uy * 6)
        out += f'''
        <g class="byte-blade" filter="url(#{P}glow)">
          <polygon points="{_f(ankle)} {_f(left)} {_f(tip)} {_f(mid)}" fill="url(#{P}crysL)"/>
          <polygon points="{_f(ankle)} {_f(right)} {_f(tip)} {_f(mid)}" fill="url(#{P}crysR)"/>
          <polygon points="{_f(ankle)} {_f(left)} {_f(tip)} {_f(right)}" fill="none" stroke="#1d4fa0" stroke-width="1.5" stroke-linejoin="round"/>
        </g>'''
    else:
        (bx, by), (ux, uy), L = _norm(ankle, foot)
        w = 3.4
        out += f'''
        <polygon points="{ankle[0]+bx*w:.1f} {ankle[1]+by*w:.1f} {_f(foot)} {ankle[0]-bx*w:.1f} {ankle[1]-by*w:.1f}" fill="#24237a" stroke="{OUT}" stroke-width="1.8" stroke-linejoin="round"/>'''
    out += f'''
        <circle cx="{ankle[0]:.1f}" cy="{ankle[1]:.1f}" r="3.2" fill="{GOLD}" stroke="{OUT}" stroke-width="1.6"/>
        <circle cx="{knee[0]:.1f}" cy="{knee[1]:.1f}" r="5" fill="{GOLD}" stroke="{OUT}" stroke-width="2"/>
        <circle cx="{knee[0]-1.4:.1f}" cy="{knee[1]-1.4:.1f}" r="1.5" fill="#ffe2a0"/>
      </g>'''
    return out


LEGS = {  # (quadril, joelho, pé) do lado esquerdo; o direito é espelhado
    4: ((-22, -4), (-98, -30), (-128, 62)),
    3: ((-24, 2), (-86, -46), (-108, 68)),
    2: ((-24, 8), (-62, -42), (-78, 72)),
    1: ((-20, 20), (-58, 2), (-44, 68)),
}


def _legs(ks, P, blades=(1,)):
    s = ""
    for k in ks:
        h, kn, ft = LEGS[k]
        m = lambda q: (-q[0], q[1])
        s += _leg(h, kn, ft, P, k in blades) + _leg(m(h), m(kn), m(ft), P, k in blades)
    return s


def _horn(base, tip, P):
    (nx, ny), _, _ = _norm(base, tip)
    w = 5
    a = (base[0] + nx * w, base[1] + ny * w); b = (base[0] - nx * w, base[1] - ny * w)
    mid = _lerp(base, tip, .45)
    return (f'<g class="byte-blade" filter="url(#{P}glow)">'
            f'<polygon points="{_f(a)} {_f(tip)} {_f(mid)}" fill="url(#{P}crysL)"/>'
            f'<polygon points="{_f(b)} {_f(tip)} {_f(mid)}" fill="url(#{P}crysR)"/>'
            f'<polygon points="{_f(a)} {_f(tip)} {_f(b)}" fill="none" stroke="#1d4fa0" stroke-width="1.4" stroke-linejoin="round"/></g>')


def _spiral(cx, cy, r0, r1, turns):
    pts = []
    n = 60
    for i in range(n + 1):
        t = i / n
        a = -math.pi / 2 + t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + " L".join(_f(p) for p in pts)


# cachecol: faixa no rosto + duas pontas rasgadas que sobem pela esquerda
TAIL1 = ["M-30 14 C-52 4 -58 -26 -74 -44 C-82 -54 -96 -58 -108 -70 L-100 -56 L-112 -60 C-96 -40 -80 -34 -70 -18 C-60 -2 -46 14 -28 24 Z",
         "M-30 14 C-56 8 -66 -18 -78 -36 C-88 -50 -104 -48 -118 -56 L-106 -46 L-118 -44 C-100 -30 -84 -30 -72 -14 C-62 0 -46 14 -28 24 Z",
         "M-30 14 C-52 4 -58 -26 -74 -44 C-82 -54 -96 -58 -108 -70 L-100 -56 L-112 -60 C-96 -40 -80 -34 -70 -18 C-60 -2 -46 14 -28 24 Z"]
TAIL2 = ["M-28 20 C-46 26 -70 18 -86 4 C-94 -2 -104 -2 -114 -8 L-108 2 L-120 4 C-104 14 -90 22 -74 26 C-58 30 -42 30 -26 28 Z",
         "M-28 20 C-48 22 -70 10 -88 8 C-98 8 -108 12 -118 10 L-110 18 L-120 24 C-104 28 -90 30 -74 32 C-58 34 -42 32 -26 28 Z",
         "M-28 20 C-46 26 -70 18 -86 4 C-94 -2 -104 -2 -114 -8 L-108 2 L-120 4 C-104 14 -90 22 -74 26 C-58 30 -42 30 -26 28 Z"]


def spider(P="BYTE", stage=1):
    bl = (1, 2) if stage >= 2 else (1,)
    s = f'''
    <g class="byte-breath">
      <ellipse cx="0" cy="76" rx="124" ry="9" fill="#000" opacity=".4"/>
      {_legs([4, 3], P, bl)}
      <!-- ponta de trás do cachecol -->
      <path fill="url(#{P}silk)" fill-opacity=".75" stroke="#5a6fc4" stroke-width="1.3" stroke-linejoin="round" d="{TAIL2[0]}">
        <animate attributeName="d" dur="1.9s" repeatCount="indefinite" begin="-.5s" values="{';'.join(TAIL2)}"/>
      </path>
      {{CREST}}
      <!-- abdômen com a runa espiral -->
      <circle cx="0" cy="-40" r="52" fill="url(#{P}abd)" stroke="{OUT}" stroke-width="2.6"/>
      <path d="M-40 -66 Q-26 -86 0 -91" stroke="#6f78ff" stroke-width="2.6" fill="none" stroke-linecap="round" opacity=".8"/>
      <circle class="byte-rune" cx="0" cy="-52" r="26" fill="url(#{P}runeglow)"/>
      <path class="byte-rune" d="{_spiral(0, -52, 1.5, 17, 2.3)}" stroke="#5fb8ff" stroke-width="3.4" fill="none" stroke-linecap="round" filter="url(#{P}glow)"/>
      {_plate((-44, -58), (-1, -1.2), 9, P)}
      {_plate((44, -58), (1, -1.2), 9, P)}
      {_plate((-50, -30), (-1, .2), 7, P)}
      {_plate((50, -30), (1, .2), 7, P)}
      {_legs([2, 1], P, bl)}
      <!-- cabeça -->
      <ellipse cx="0" cy="10" rx="38" ry="31" fill="url(#{P}head)" stroke="{OUT}" stroke-width="2.6"/>
      <path d="M-24 -10 Q-14 -20 4 -21" stroke="#6f78ff" stroke-width="2.2" fill="none" stroke-linecap="round" opacity=".8"/>
      {_plate((-36, 0), (-.6, -1), 7, P)}
      {_plate((36, 0), (.6, -1), 7, P)}
      {{HORNS}}
      <!-- 6 olhos pequenos luminosos -->
      <g filter="url(#{P}glow)">
        <circle class="byte-mini" cx="-5" cy="-12" r="2.7" fill="#7cd0ff"/>
        <circle class="byte-mini" cx="5" cy="-12" r="2.7" fill="#7cd0ff"/>
        <circle class="byte-mini m2" cx="-14" cy="-8" r="2.4" fill="#7cd0ff"/>
        <circle class="byte-mini m2" cx="14" cy="-8" r="2.4" fill="#7cd0ff"/>
        <circle class="byte-mini m3" cx="-23" cy="-3" r="2" fill="#7cd0ff"/>
        <circle class="byte-mini m3" cx="23" cy="-3" r="2" fill="#7cd0ff"/>
      </g>
      <!-- 2 olhos grandes âmbar -->
      <g class="byte-eyes">
        <circle cx="-14" cy="11" r="11.5" fill="url(#{P}eye)" stroke="{OUT}" stroke-width="2.2"/>
        <circle cx="14" cy="11" r="11.5" fill="url(#{P}eye)" stroke="{OUT}" stroke-width="2.2"/>
        <ellipse cx="-12" cy="12.5" rx="5" ry="6.4" fill="#120800"/>
        <ellipse cx="12" cy="12.5" rx="5" ry="6.4" fill="#120800"/>
        <circle cx="-17" cy="8.5" r="2.6" fill="#fff"/>
        <circle cx="9" cy="8.5" r="2.6" fill="#fff"/>
        <circle cx="-9" cy="16" r="1.1" fill="#fff" opacity=".8"/>
        <circle cx="15" cy="16" r="1.1" fill="#fff" opacity=".8"/>
      </g>
      <!-- pálpebras (expressão determinada) -->
      <path d="M-28 2 Q-15 -1 -1 6 L-1 -2 L-28 -2 Z" fill="#23227a"/><path d="M-27 2 Q-15 -1 -1 6" stroke="{OUT}" stroke-width="2.6" fill="none" stroke-linecap="round"/>
      <path d="M28 2 Q15 -1 1 6 L1 -2 L28 -2 Z" fill="#23227a"/><path d="M27 2 Q15 -1 1 6" stroke="{OUT}" stroke-width="2.6" fill="none" stroke-linecap="round"/>
      <!-- presas -->
      <path d="M-9 34 Q-11 45 -5 50 Q-6 42 -3 35 Z" fill="#eef0ff" stroke="{OUT}" stroke-width="1.6"/>
      <path d="M9 34 Q11 45 5 50 Q6 42 3 35 Z" fill="#eef0ff" stroke="{OUT}" stroke-width="1.6"/>
      <!-- cachecol de seda (rasgado) -->
      <path fill="url(#{P}silk)" fill-opacity=".9" stroke="#5a6fc4" stroke-width="1.4" stroke-linejoin="round" d="{TAIL1[0]}">
        <animate attributeName="d" dur="1.6s" repeatCount="indefinite" values="{';'.join(TAIL1)}"/>
      </path>
      <path d="M-37 18 Q0 36 37 18 L38 27 L33 32 L29 29 Q0 43 -14 39 L-18 44 L-23 38 Q-33 35 -38 28 Z" fill="url(#{P}silk)" stroke="#5a6fc4" stroke-width="1.6" stroke-linejoin="round"/>
      <path d="M-34 22 Q0 39 34 22" stroke="#eef3ff" stroke-width="1.2" fill="none" opacity=".8"/>
      <path d="M-26 30 Q-4 40 20 33" stroke="#6f86d8" stroke-width="1" fill="none" opacity=".8"/>
    </g>'''
    crest = horns = ""
    if stage >= 2:
        crest = _plate((-18, -92), (-.4, -1), 8, P) + _plate((18, -92), (.4, -1), 8, P) + _plate((0, -98), (0, -1), 9, P)
        horns = _horn((-20, -16), (-34, -42), P) + _horn((20, -16), (34, -42), P)
    s = s.replace("{CREST}", crest).replace("{HORNS}", horns)
    return s.replace("BYTE", P)
