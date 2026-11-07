"""Builds the README images. Stdlib only, so the hourly Action can run it."""
import base64
import datetime as dt
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "img"

GREEN = ("#172810", "#1d3214", "#263c17")
CREAM = "#f3e3c3"
TEXT = "#f5ebdd"


def font(name, family):
    data = base64.b64encode((ASSETS / "fonts" / f"{name}.woff2").read_bytes()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{data}) format('woff2');}}"


def fonts(*names):
    families = {"allura": "Allura", "caveat": "Caveat", "bricolage": "Bricolage", "inter": "Inter", "barlow": "Barlow"}
    return "".join(font(n, families[n]) for n in names)


def contours(width, height, count, opacity=0.07):
    # periodic in x every 1000px so the drift loops seamlessly
    paths = []
    for k in range(count):
        base = -40 + k * 24
        pts = []
        for x in range(-1000, width + 1001, 16):
            y = base + 30 * math.sin(2 * math.pi * x / 1000 + k * 0.35) + 16 * math.sin(2 * math.pi * x / 500 - k * 0.5)
            pts.append(f"{x},{y:.1f}")
        paths.append(f'<polyline points="{" ".join(pts)}"/>')
    return (
        f'<g fill="none" stroke="{CREAM}" stroke-opacity="{opacity}" stroke-width="1.2">'
        '<animateTransform attributeName="transform" type="translate" from="0 0" to="-1000 0" dur="80s" repeatCount="indefinite"/>'
        + "".join(paths) + "</g>"
    )


def backdrop(width, height, radius=22):
    return f"""
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0.3">
      <stop offset="0" stop-color="{GREEN[0]}"/><stop offset=".5" stop-color="{GREEN[1]}"/><stop offset="1" stop-color="{GREEN[2]}"/>
    </linearGradient>
    <radialGradient id="glow" cx="1" cy="0" r=".8"><stop offset="0" stop-color="#6e782d" stop-opacity=".25"/><stop offset="1" stop-color="#6e782d" stop-opacity="0"/></radialGradient>
    <clipPath id="frame"><rect width="{width}" height="{height}" rx="{radius}"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{width}" height="{height}" fill="url(#bg)"/>
    <rect width="{width}" height="{height}" fill="url(#glow)"/>
    {contours(width, height, height // 24 + 4)}
  </g>"""


def svg(width, height, style, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f"<style>{style}</style>{body}</svg>\n"
    )


def hero():
    w, h = 1000, 360
    style = fonts("allura", "caveat", "inter") + f"""
    .hi {{ font: 700 34px Caveat; fill: {CREAM}; }}
    .tag {{ font: 92px Allura; fill: {CREAM}; }}
    .ban {{ font: 500 19px Inter; fill: {TEXT}; }}
    .soft {{ fill-opacity: .6; }}
    .note {{ font: 700 32px Caveat; fill: {CREAM}; }}
    .ink {{ fill: none; stroke: {CREAM}; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }}
    .blink {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}"""

    def rise(delay):
        return (f'opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur=".9s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 14" to="0 0" begin="{delay}s" dur=".9s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>')

    body = backdrop(w, h) + f"""
  <g {rise(0)}<text class="hi" x="70" y="78" transform="rotate(-3 70 78)">hey, I'm Grishon</text></g>
  <g {rise(.25)}<text class="tag" x="62" y="172">Limitations are</text></g>
  <g {rise(.5)}<text class="tag" x="132" y="252">Perceptions</text></g>
  <clipPath id="type"><rect x="60" y="280" height="40" width="0">
    <animate attributeName="width" from="0" to="700" begin="1.1s" dur="1.6s" fill="freeze"/>
  </rect></clipPath>
  <text class="ban" x="72" y="306" clip-path="url(#type)">Full stack engineer. Writes code, ships things, <tspan class="soft">occasionally touches grass.</tspan></text>
  <rect class="blink" x="72" y="290" width="2" height="22" fill="{CREAM}">
    <animate attributeName="x" from="72" to="752" begin="1.1s" dur="1.6s" fill="freeze"/>
  </rect>
  <g {rise(2.2)}<g transform="rotate(5 800 90)">
    <text class="note" x="700" y="92">scroll down,</text>
    <text class="note" x="700" y="128">I built stuff</text>
  </g></g>
  <path class="ink" stroke-dasharray="260" stroke-dashoffset="260" d="M842 140 C 880 170, 880 220, 846 262 M832 246 L846 263 L862 250">
    <animate attributeName="stroke-dashoffset" from="260" to="0" begin="2.6s" dur="1.2s" fill="freeze"/>
  </path>"""
    return svg(w, h, style, body)


def tile(card, note, note_y, arrow, wobble):
    w, h = 490, 380
    style = fonts("caveat", "bricolage", "inter", "barlow") + f"""
    .note {{ font: 700 27px Caveat; fill: {CREAM}; }}
    .ink {{ fill: none; stroke: {CREAM}; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }}"""
    note_svg = "".join(f'<text class="note" x="{x}" y="{note_y + i * 30}">{line}</text>' for i, (x, line) in enumerate(note))
    body = backdrop(w, h) + f"""
  <g transform="translate(245 {wobble[0]})">
    <g>
      <animateTransform attributeName="transform" type="rotate" values="{wobble[1]};{wobble[1] + 2.5};{wobble[1]}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
      <rect x="-140" y="-112" width="280" height="236" rx="16" fill="#000" opacity=".35" transform="translate(0 14)" filter="url(#soft)"/>
      {card}
      <rect x="-44" y="-126" width="88" height="26" fill="{CREAM}" fill-opacity=".6" transform="rotate({-wobble[1] * 1.6})"/>
    </g>
  </g>
  <defs><filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter></defs>
  {note_svg}
  <path class="ink" d="{arrow}"/>"""
    return svg(w, h, style, body)


def flapjack():
    card = """
      <rect x="-140" y="-112" width="280" height="236" rx="16" fill="#fbf6ec"/>
      <g transform="translate(-118 -92) scale(1.45)">
        <rect x="0" y="17" width="30" height="7" rx="3.5" fill="#b4561b"/><rect x="3" y="9.5" width="26" height="7" rx="3.5" fill="#d9853b"/><rect x="6" y="2" width="21" height="7" rx="3.5" fill="#f2c14e"/>
      </g>
      <text x="-66" y="-58" style="font:700 36px Bricolage;letter-spacing:-1px" fill="#2a1d14">flapjack</text>
      <g style="font:700 24px Bricolage;letter-spacing:-.4px" fill="#2a1d14">
        <text x="-118" y="-6">The notetaker that</text>
        <text x="-118" y="22">actually gets</text>
        <text x="-118" y="50" fill="#b4561b">shit done.</text>
      </g>
      <text x="-118" y="102" style="font:500 13px Inter" fill="#7d6b5b">getflapjack.com</text>
      <g transform="translate(70 98)"><circle r="4.5" fill="#c8364f"/><circle cx="14" r="4.5" fill="#2e8a63"/><circle cx="28" r="4.5" fill="#3f6fc4"/><circle cx="42" r="4.5" fill="#9c8e7e"/></g>"""
    note = [(46, "built this cos my to-do list"), (46, "was a crime scene")]
    arrow = "M330 52 C 372 56, 384 84, 368 116 M356 104 L368 117 L380 102"
    return tile(card, note, 46, arrow, (226, -6))


def urbanlugs():
    logo = (ASSETS / "urbanlugs-logo.svg").read_text()
    logo = re.sub(r"<\?xml.*?\?>|<!--.*?-->", "", logo, flags=re.S)
    logo = logo.replace(".st0", ".ul0").replace(".st1", ".ul1").replace('class="st0"', 'class="ul0"').replace('class="st1"', 'class="ul1"')
    logo = re.sub(r"<svg[^>]*>", '<svg x="-126" y="-96" width="210" height="41" viewBox="0 0 366.1 71.1">', logo, count=1)
    card = f"""
      <clipPath id="ulcard"><rect x="-140" y="-112" width="280" height="236" rx="16"/></clipPath>
      <rect x="-140" y="-112" width="280" height="236" rx="16" fill="#0a0a0a" stroke="#222"/>
      <rect x="-140" y="-112" width="280" height="5" fill="#3DB320" clip-path="url(#ulcard)"/>
      {logo}
      <g style="font:700 28px Barlow;letter-spacing:.6px">
        <text x="-118" y="2" fill="#fff">PREMIUM CUSTOM</text>
        <text x="-118" y="34" fill="#3DB320">FORGED WHEELS.</text>
      </g>
      <text x="-118" y="102" style="font:700 15px Barlow;letter-spacing:1.4px" fill="#8a8a8a">URBANLUGS.COM</text>"""
    note = [(128, "and this, cos cars deserve"), (128, "nice shoes too")]
    arrow = "M106 330 C 74 326, 66 300, 82 274 M70 284 L82 273 L94 284"
    return tile(card, note, 322, arrow, (150, 5))


MOODS = [
    (range(0, 5), ["Probably still debugging something I swore was fixed.", "Should be asleep. Is not asleep."]),
    (range(5, 8), ["Coffee first. Opinions later.", "Pretending the alarm didn't go off."]),
    (range(8, 12), ["Shipping. Or in a meeting about shipping.", "Deep in a PR. Send snacks."]),
    (range(12, 14), ["Lunch. The code can wait. Briefly.", "Eating at my desk like a professional."]),
    (range(14, 18), ["Writing code future me will judge.", "Afternoon slump, fixed with more coffee."]),
    (range(18, 21), ["Off the clock. Mostly. Fine, a little bit on.", "Planning a hitch-hike I will never take."]),
    (range(21, 24), ["Side-project hours. Flapjack gets the night shift.", "Saying \"one last commit\" for the third time."]),
]


def now(moment=None):
    moment = moment or dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))
    hour = moment.hour
    mood = next(lines for hours, lines in MOODS if hour in hours)[moment.timetuple().tm_yday % 2]
    clock = f"{(hour % 12) or 12}{'am' if hour < 12 else 'pm'}"
    w, h = 1000, 110
    style = fonts("caveat", "inter") + f"""
    .t {{ font: 700 32px Caveat; fill: {CREAM}; }}
    .m {{ font: 500 18px Inter; fill: {TEXT}; fill-opacity: .8; }}
    .s {{ font: 500 12px Inter; fill: {CREAM}; fill-opacity: .45; letter-spacing: 1.6px; }}"""
    body = backdrop(w, h, 18) + f"""
  <circle cx="44" cy="55" r="7" fill="#3DB320"/>
  <circle cx="44" cy="55" r="7" fill="none" stroke="#3DB320" stroke-width="2">
    <animate attributeName="r" values="7;18" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text class="t" x="72" y="50">It's around {clock} in Nairobi.</text>
  <text class="m" x="72" y="80">{mood.replace('"', "&quot;")}</text>
  <text class="s" x="{w - 32}" y="96" text-anchor="end">UPDATES EVERY HOUR</text>"""
    return svg(w, h, style, body)


JOBS = [
    ("2020", "Techxers Kenya", "software engineer"),
    ("2021", "Bloow Global", "MVP to 80k users"),
    ("2022", "Ada Labs Africa", "hired 10+ engineers"),
    ("2022", "Chrome Lot", "solo dev to a team of 5"),
    ("2024", "Cigna Healthcare", "a health app for Saudi Arabia"),
    ("now", "Greenspoon", "senior software engineer"),
]


def trail(ink):
    w, h = 1000, 250
    mid = 125
    xs = [95 + i * 158 for i in range(len(JOBS))]
    pts = []
    for x in range(20, w - 19, 10):
        pts.append(f"{x},{mid + 16 * math.sin(x / 70) + 8 * math.sin(x / 31):.1f}")
    y_at = lambda x: mid + 16 * math.sin(x / 70) + 8 * math.sin(x / 31)
    style = fonts("caveat", "inter") + f"""
    .yr {{ font: 700 26px Caveat; fill: #3DB320; }}
    .co {{ font: 500 16px Inter; fill: {ink}; }}
    .nt {{ font: 700 21px Caveat; fill: {ink}; fill-opacity: .7; }}"""
    stops = []
    for i, ((year, company, note), x) in enumerate(zip(JOBS, xs)):
        y = y_at(x)
        up = i % 2 == 0
        ty = y - 34 if up else y + 44
        begin = .4 + i * .3
        now = year == "now"
        pulse = (f'<circle cx="{x}" cy="{y:.1f}" r="8" fill="none" stroke="#3DB320" stroke-width="2">'
                 '<animate attributeName="r" values="8;22" dur="1.8s" repeatCount="indefinite"/>'
                 '<animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>') if now else ""
        text = (f'<text class="yr" x="{x}" y="{ty - (40 if up else 0):.1f}" text-anchor="middle">{year}</text>'
                f'<text class="co" x="{x}" y="{ty - (16 if up else -22):.1f}" text-anchor="middle">{company}</text>'
                f'<text class="nt" x="{x}" y="{ty + (8 if up else 46):.1f}" text-anchor="middle">{note}</text>')
        stops.append(
            f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{begin:.1f}s" dur=".5s" fill="freeze"/>'
            f'{pulse}<circle cx="{x}" cy="{y:.1f}" r="{8 if now else 6}" fill="{"#3DB320" if now else ink}"/>{text}</g>')
    body = f"""
  <polyline points="{" ".join(pts)}" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="6 7"/>
  {"".join(stops)}"""
    return svg(w, h, style, body)


HEADINGS = {"built": "stuff I've built", "work": "where I've worked", "adventure": "choose your own adventure"}


def heading(text, ink):
    w, h = 16 * len(text) + 30, 72
    end = 15.5 * len(text)
    style = fonts("caveat") + f".h {{ font: 700 44px Caveat; fill: {ink}; }}"
    body = f"""
  <text class="h" x="4" y="44">{text}</text>
  <path d="M6 60 C {end * .25:.0f} 52, {end * .5:.0f} 66, {end * .75:.0f} 57 S {end - 20} 54, {end} 58" fill="none" stroke="#3DB320" stroke-width="3.2" stroke-linecap="round"
    stroke-dasharray="{end * 1.2:.0f}" stroke-dashoffset="{end * 1.2:.0f}">
    <animate attributeName="stroke-dashoffset" from="{end * 1.2:.0f}" to="0" begin=".3s" dur=".9s" fill="freeze"/>
  </path>"""
    return svg(w, h, style, body)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, build in {"hero": hero, "flapjack": flapjack, "urbanlugs": urbanlugs, "now": now}.items():
        (OUT / f"{name}.svg").write_text(build())
    (OUT / "work-dark.svg").write_text(trail(CREAM))
    (OUT / "work-light.svg").write_text(trail("#1d3214"))
    for key, text in HEADINGS.items():
        (OUT / f"h-{key}-dark.svg").write_text(heading(text, CREAM))
        (OUT / f"h-{key}-light.svg").write_text(heading(text, "#1d3214"))
