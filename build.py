"""Render the neofetch-style profile card (dark_mode.svg, light_mode.svg).

Left: an analysis board, Kasparov–Topalov, Wijk aan Zee 1999, before
24.Rxd4!! (position checked move by move with python-chess).
Right: profile info plus live numbers from stats.json (tools/stats.py).
Run from the repo root.
"""
import json
from xml.sax.saxutils import escape

WIDTH = 56  # characters per info line

# (key, value); None is a blank line, a str is a section header
INFO = [
    ("Role", "AI Engineer"),
    ("Mission", "Data → Knowledge → Decision → Action"),
    ("Focus.Work", "Enterprise intelligence platforms"),
    ("Focus.Play", "Human-like chess engines"),
    ("Workflow", "AI agents as teammates (Claude, Codex)"),
    ("Interface", "Persian-first, RTL-native"),
    None,
    ("Languages.Code", "TypeScript, Python, JavaScript"),
    ("Languages.Real", "Persian, English"),
    ("Stack.Web", "Next.js, React, NestJS, FastAPI"),
    ("Stack.Data", "PostgreSQL, Prisma, Redis, DuckDB"),
    ("Stack.AI", "PyTorch, ONNX, RAG, agents"),
    ("Stack.Ops", "Docker, GitHub Actions, Ansible"),
    None,
    "Chess",
    ("Olympiad", "Iran women's team analyst · Samarkand"),
    ("Now", "Preparation & analysis for grandmasters"),
    ("Engine", "ar-karkon1 · SE-ResNet → ONNX → UCI"),
    ("Analysis", "PGN → Stockfish → DuckDB → dossier"),
    ("Motto", "Similarity over accuracy"),
    ("Chess.com", "arinlasp"),
    None,
    "GitHub Stats",
]

THEMES = {
    "dark": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", value="#a5d6ff",
                 cc="#616e7f", accent="#3fb950",
                 sq_light="#3a4250", sq_dark="#262d37", hl="#ffa657",
                 white="#f0f6fc", white_edge="#0d1117", black="#0d1117", black_edge="#9da7b3"),
    "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", value="#0a3069",
                  cc="#8c959f", accent="#1a7f37",
                  sq_light="#e3e8ee", sq_dark="#b4c0cc", hl="#d4a72c",
                  white="#ffffff", white_edge="#24292f", black="#24292f", black_edge="#24292f"),
}

W = 985
INFO_X, INFO_Y, LINE = 440, 30, 20

FEN = "b2r3r/k4p1p/p2q1np1/NppP4/3p1Q2/P4PPB/1PP4P/1K1RR3"
LAST_MOVE = ("e7", "d6")          # 23...Qd6
ARROW = ("d1", "d4")              # 24.Rxd4!!
GAME = "Kasparov – Topalov · Wijk aan Zee 1999"
MOVES = [
    "24.Rxd4!! cxd4 25.Re7+ Kb6 26.Qxd4+ Kxa5",
    "27.b4+ Ka4 28.Qc3 Qxd5 29.Ra7 Bb7 30.Rxb7 … 1-0",
]
TAGLINE = "engines find the best move · I model the human one"

BOARD_X, BOARD_Y, SQ = 40, 48, 44
GLYPHS = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟\ufe0e"}
PIECE_FONT = "'DejaVu Sans','Segoe UI Symbol','Apple Symbols','Noto Sans Symbols 2',serif"


def square_xy(name):
    file, rank = ord(name[0]) - ord("a"), int(name[1])
    return BOARD_X + file * SQ, BOARD_Y + (8 - rank) * SQ


def board(t):
    out = []
    for r in range(8):
        for f in range(8):
            fill = t["sq_light"] if (r + f) % 2 == 0 else t["sq_dark"]
            out.append(f'<rect x="{BOARD_X + f * SQ}" y="{BOARD_Y + r * SQ}" width="{SQ}" height="{SQ}" fill="{fill}"/>')
    for name in LAST_MOVE:
        x, y = square_xy(name)
        out.append(f'<rect x="{x}" y="{y}" width="{SQ}" height="{SQ}" fill="{t["hl"]}" opacity="0.38"/>')
    out.append(f'<rect x="{BOARD_X}" y="{BOARD_Y}" width="{8 * SQ}" height="{8 * SQ}" fill="none" '
               f'stroke="{t["cc"]}" stroke-width="1"/>')

    for r, row in enumerate(FEN.split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
                continue
            white = ch.isupper()
            cx, cy = BOARD_X + f * SQ + SQ / 2, BOARD_Y + r * SQ + SQ * 0.80
            fill, edge = (t["white"], t["white_edge"]) if white else (t["black"], t["black_edge"])
            out.append(f'<text x="{cx}" y="{cy}" text-anchor="middle" font-family="{PIECE_FONT}" '
                       f'font-size="{SQ * 0.82:.0f}px" fill="{fill}" stroke="{edge}" stroke-width="0.9" '
                       f'paint-order="stroke">{GLYPHS[ch.lower()]}</text>')
            f += 1

    (x1, y1), (x2, y2) = (square_xy(s) for s in ARROW)
    x1 += SQ / 2; x2 += SQ / 2; y1 += SQ / 2; y2 += SQ * 0.95
    out.append(f'<marker id="head" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="3" markerHeight="3" '
               f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{t["accent"]}"/></marker>')
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["accent"]}" stroke-width="9" '
               f'stroke-linecap="round" opacity="0.85" marker-end="url(#head)"/>')

    for i in range(8):
        out.append(f'<text x="{BOARD_X - 12}" y="{BOARD_Y + i * SQ + SQ / 2 + 4}" font-size="11px" '
                   f'class="cc" text-anchor="middle">{8 - i}</text>')
        out.append(f'<text x="{BOARD_X + i * SQ + SQ / 2}" y="{BOARD_Y + 8 * SQ + 15}" font-size="11px" '
                   f'class="cc" text-anchor="middle">{"abcdefgh"[i]}</text>')

    out.append(f'<text x="{BOARD_X - 20}" y="32" font-size="13px"><tspan class="key">♟ analysis</tspan>'
               f'<tspan class="cc"> · </tspan><tspan class="value">{escape(GAME)}</tspan></text>')
    y = BOARD_Y + 8 * SQ + 45
    for i, line in enumerate(MOVES):
        out.append(f'<text x="{BOARD_X - 20}" y="{y + i * 19}" font-size="12.5px" fill="{t["fg"]}">{escape(line)}</text>')
    out.append(f'<text x="{BOARD_X - 20}" y="{y + len(MOVES) * 19 + 14}" font-size="12.5px" class="accent">'
               f'{escape(TAGLINE)}</text>')
    return out


def kv(key, value):
    dots = WIDTH - len(key) - len(value) - 3
    return (f'<tspan class="key">{escape(key)}</tspan>:'
            f'<tspan class="cc"> {"." * dots} </tspan>'
            f'<tspan class="value">{escape(value)}</tspan>')


def header(title):
    return f'- {escape(title)} <tspan class="cc">{"—" * (WIDTH - len(title) - 3)}</tspan>'


def stats_lines(s):
    left = f'<tspan class="key">Contributions</tspan>: <tspan class="value">{s["contributions"]}</tspan> (12 mo)'
    right = f'<tspan class="key">Active days</tspan>: <tspan class="value">{s["active_days"]}</tspan>'
    streak = (f'<tspan class="key">Streak</tspan>: <tspan class="value">{s["current_streak"]}</tspan> days'
              f' <tspan class="cc">|</tspan> <tspan class="key">Longest</tspan>:'
              f' <tspan class="value">{s["longest_streak"]}</tspan> days')
    updated = f'<tspan class="cc">updated {escape(s["updated"])} · refreshed daily by GitHub Actions</tspan>'
    return [f'{left} <tspan class="cc">|</tspan> {right}', streak, updated]


def svg(theme, stats):
    t = THEMES[theme]
    lines = [f'<tspan class="accent">alireza</tspan>@<tspan class="accent">karkon</tspan> '
             f'<tspan class="cc">{"—" * (WIDTH - 15)}</tspan>']
    for item in INFO:
        if item is None:
            lines.append("")
        elif isinstance(item, str):
            lines.append(header(item))
        else:
            lines.append(kv(*item))
    lines += stats_lines(stats)
    H = INFO_Y + (len(lines) - 1) * LINE + 25

    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{W}px" height="{H}px" font-size="15px">',
        "<style>",
        "@font-face {src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback';"
        " font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%;}",
        f".key {{fill: {t['key']};}} .value {{fill: {t['value']};}} .cc {{fill: {t['cc']};}}"
        f" .accent {{fill: {t['accent']};}}",
        "text, tspan {white-space: pre;}",
        "</style>",
        f'<rect width="{W}px" height="{H}px" fill="{t["bg"]}" rx="15"/>',
    ]
    out += board(t)

    out.append(f'<text x="{INFO_X}" y="{INFO_Y}" fill="{t["fg"]}">')
    for i, line in enumerate(lines):
        out.append(f'<tspan x="{INFO_X}" y="{INFO_Y + i * LINE}">{line}</tspan>')
    out.append("</text>\n</svg>")
    return "\n".join(out)


def main():
    with open("stats.json") as f:
        stats = json.load(f)
    for theme in THEMES:
        with open(f"{theme}_mode.svg", "w") as f:
            f.write(svg(theme, stats))


main()
