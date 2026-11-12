#!/usr/bin/env python3
"""Generate studio-style product renders (SVG -> PNG via headless Chrome).

Usage: python3 -I scripts/render_products.py <repo_root>
Output: assets/images/products/<sku>[-<color>].png  (1000x1000)
        assets/images/categories/<slug>.png         (600x600, transparent bg)
All artwork is original (drawn here), so there are no licensing issues.
"""
import json, os, subprocess, sys, tempfile, concurrent.futures as cf

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_P = os.path.join(ROOT, "assets/images/products")
OUT_C = os.path.join(ROOT, "assets/images/categories")
OUT_X = os.path.join(ROOT, "assets/images/cutouts")  # transparent, for banners


def shade(hex_, f):
    """f<0 darker, f>0 lighter."""
    h = hex_.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if f < 0:
        r, g, b = (int(c * (1 + f)) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def is_light(hex_):
    h = hex_.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) > 170


def defs(c):
    return f"""
<defs>
 <linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{shade(c, .25)}"/><stop offset=".55" stop-color="{c}"/><stop offset="1" stop-color="{shade(c, -.35)}"/></linearGradient>
 <linearGradient id="bodyV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{shade(c, .3)}"/><stop offset="1" stop-color="{shade(c, -.3)}"/></linearGradient>
 <linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff8a3d"/><stop offset=".45" stop-color="#ff6a00"/><stop offset=".46" stop-color="#2b2b2b"/><stop offset="1" stop-color="#111"/></linearGradient>
 <linearGradient id="screen2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f1f23"/><stop offset=".6" stop-color="#111"/><stop offset="1" stop-color="#ff6a00"/></linearGradient>
 <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff6a00" stop-opacity=".18"/><stop offset="1" stop-color="#ff6a00" stop-opacity="0"/></radialGradient>
 <linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="18"/></filter>
 <filter id="soft"><feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#000" flood-opacity=".22"/></filter>
</defs>"""


def floor(cx=500, cy=880, rx=300, ry=34):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity=".18" filter="url(#sh)"/>'


def ui_lines(x, y, w, n=3, col="#fff", op=.5):
    s = ""
    for i in range(n):
        s += f'<rect x="{x}" y="{y + i * 28}" width="{w * (1 - i * .22)}" height="12" rx="6" fill="{col}" opacity="{op}"/>'
    return s


# ── device drawings (1000x1000 canvas) ────────────────────────────────
def phone(c):
    return floor(rx=200) + f"""
<g filter="url(#soft)">
 <rect x="330" y="110" width="300" height="640" rx="54" fill="{shade(c, -.45)}" transform="rotate(-8 480 430)"/>
 <rect x="342" y="122" width="276" height="616" rx="44" fill="url(#body)" transform="rotate(-8 480 430)"/>
 <g transform="rotate(-8 480 430)">
  <rect x="372" y="152" width="104" height="150" rx="34" fill="{shade(c, -.25)}" opacity=".9"/>
  <circle cx="404" cy="190" r="22" fill="#111"/><circle cx="404" cy="190" r="12" fill="#2a3b55"/>
  <circle cx="404" cy="260" r="22" fill="#111"/><circle cx="404" cy="260" r="12" fill="#2a3b55"/>
  <circle cx="450" cy="225" r="16" fill="#111"/><circle cx="450" cy="225" r="8" fill="#2a3b55"/>
 </g>
</g>
<g filter="url(#soft)">
 <rect x="440" y="180" width="300" height="640" rx="54" fill="#0c0c0d"/>
 <rect x="452" y="192" width="276" height="616" rx="44" fill="url(#screen)"/>
 <rect x="555" y="210" width="70" height="20" rx="10" fill="#000"/>
 <text x="590" y="330" fill="#fff" font-family="Poppins,Arial" font-weight="700" font-size="64" text-anchor="middle">12:30</text>
 {ui_lines(490, 640, 200)}
 <rect x="452" y="192" width="276" height="616" rx="44" fill="url(#gloss)"/>
</g>"""


def flip(c):
    return floor(rx=190) + f"""
<g filter="url(#soft)" transform="rotate(-6 500 500)">
 <rect x="360" y="140" width="280" height="330" rx="40" fill="url(#body)"/>
 <rect x="380" y="160" width="240" height="250" rx="28" fill="url(#screen2)"/>
 <circle cx="430" cy="430" r="20" fill="#111"/><circle cx="480" cy="430" r="20" fill="#111"/>
 <rect x="360" y="468" width="280" height="22" rx="8" fill="{shade(c, -.4)}"/>
 <rect x="360" y="490" width="280" height="330" rx="40" fill="url(#bodyV)"/>
 <rect x="372" y="502" width="256" height="306" rx="30" fill="#111"/>
 <rect x="384" y="514" width="232" height="282" rx="24" fill="url(#screen)"/>
 <text x="500" y="250" fill="#fff" font-family="Poppins,Arial" font-weight="700" font-size="54" text-anchor="middle">09:41</text>
</g>"""


def laptop(c):
    return floor(cy=840, rx=380) + f"""
<g filter="url(#soft)">
 <path d="M230 230 Q230 200 260 200 L740 200 Q770 200 770 230 L770 590 L230 590 Z" fill="{shade(c, -.2)}"/>
 <rect x="248" y="218" width="504" height="356" rx="10" fill="#0b0b0c"/>
 <rect x="262" y="232" width="476" height="328" rx="4" fill="url(#screen)"/>
 <rect x="300" y="290" width="180" height="22" rx="11" fill="#fff" opacity=".85"/>
 {ui_lines(300, 330, 160)}
 <rect x="262" y="232" width="476" height="328" rx="4" fill="url(#gloss)"/>
 <path d="M150 600 L850 600 L800 680 Q795 690 780 690 L220 690 Q205 690 200 680 Z" fill="url(#bodyV)"/>
 <path d="M200 600 L800 600 L760 650 L240 650 Z" fill="{shade(c, -.15)}"/>
 <path d="M430 666 L570 666 L565 680 L435 680 Z" fill="{shade(c, -.3)}"/>
 <rect x="150" y="596" width="700" height="10" rx="5" fill="{shade(c, .35)}"/>
</g>"""


def headphones(c):
    pad = "#1d1d1f" if is_light(c) else shade(c, -.5)
    return floor(rx=240) + f"""
<g filter="url(#soft)">
 <path d="M270 560 Q260 170 500 160 Q740 170 730 560" fill="none" stroke="{shade(c, -.3)}" stroke-width="56" stroke-linecap="round"/>
 <path d="M270 560 Q260 170 500 160 Q740 170 730 560" fill="none" stroke="url(#body)" stroke-width="40" stroke-linecap="round"/>
 <rect x="232" y="470" width="44" height="120" rx="18" fill="{shade(c, -.2)}"/>
 <rect x="724" y="470" width="44" height="120" rx="18" fill="{shade(c, -.2)}"/>
 <ellipse cx="240" cy="640" rx="96" ry="140" fill="url(#body)"/>
 <ellipse cx="270" cy="640" rx="70" ry="118" fill="{pad}"/>
 <ellipse cx="760" cy="640" rx="96" ry="140" fill="url(#body)"/>
 <ellipse cx="730" cy="640" rx="70" ry="118" fill="{pad}"/>
 <ellipse cx="210" cy="600" rx="30" ry="60" fill="#fff" opacity=".18"/>
 <ellipse cx="790" cy="600" rx="30" ry="60" fill="#fff" opacity=".18"/>
</g>"""


def headset(c):
    return headphones(c) + """
<path d="M300 720 Q360 820 470 800" fill="none" stroke="#111" stroke-width="16" stroke-linecap="round"/>
<circle cx="478" cy="798" r="20" fill="#ff6a00"/>"""


def earbuds(c):
    return floor(rx=230) + f"""
<g filter="url(#soft)">
 <rect x="300" y="420" width="400" height="330" rx="120" fill="url(#body)"/>
 <path d="M300 540 L700 540" stroke="{shade(c, -.25)}" stroke-width="4"/>
 <circle cx="500" cy="650" r="9" fill="#34c759"/>
 <rect x="470" y="735" width="60" height="10" rx="5" fill="{shade(c, -.4)}"/>
</g>
<g filter="url(#soft)">
 <g transform="rotate(-20 380 300)"><ellipse cx="380" cy="260" rx="70" ry="76" fill="url(#body)"/><rect x="350" y="300" width="56" height="170" rx="28" fill="url(#body)"/><ellipse cx="345" cy="245" rx="34" ry="30" fill="#2b2b2b"/></g>
 <g transform="rotate(20 620 300)"><ellipse cx="620" cy="260" rx="70" ry="76" fill="url(#body)"/><rect x="594" y="300" width="56" height="170" rx="28" fill="url(#body)"/><ellipse cx="655" cy="245" rx="34" ry="30" fill="#2b2b2b"/></g>
</g>"""


def console(c):
    return floor(rx=280) + f"""
<g filter="url(#soft)">
 <path d="M380 150 Q500 130 560 160 L600 840 Q500 870 400 850 Z" fill="#1d1d1f"/>
 <path d="M330 170 Q390 140 450 150 L470 850 Q400 860 340 840 Q300 500 330 170 Z" fill="url(#body)"/>
 <path d="M560 160 Q640 170 680 200 Q710 520 670 840 Q620 860 600 840 Z" fill="url(#body)"/>
 <rect x="455" y="200" width="12" height="620" rx="6" fill="#ff6a00" opacity=".9"/>
</g>
{gamepad_shape('#f5f5f7', 640, 690, .45)}"""


def tower(c):
    return floor(rx=230) + f"""
<g filter="url(#soft)">
 <rect x="360" y="170" width="290" height="660" rx="26" fill="url(#body)"/>
 <rect x="390" y="190" width="230" height="140" rx="18" fill="{shade(c, -.3)}"/>
 <circle cx="505" cy="260" r="80" fill="#0b0b0c"/>
 <circle cx="505" cy="260" r="62" fill="none" stroke="#ff6a00" stroke-width="4" opacity=".7"/>
 {''.join(f'<circle cx="{440 + (i % 6) * 26}" cy="{230 + (i // 6) * 22}" r="5" fill="#000" opacity=".5"/>' for i in range(0))}
 <rect x="380" y="770" width="60" height="10" rx="5" fill="#fff" opacity=".7"/>
 <rect x="360" y="170" width="290" height="660" rx="26" fill="url(#gloss)"/>
</g>"""


def gamepad_shape(c, cx=500, cy=520, s=1.0):
    acc = "#ff6a00" if c.lower() not in ("#ff6a00",) else "#111"
    return f"""
<g filter="url(#soft)" transform="translate({cx} {cy}) scale({s}) translate(-500 -520)">
 <path d="M300 380 Q500 340 700 380 Q790 400 830 520 Q880 700 800 740 Q740 770 680 650 L320 650 Q260 770 200 740 Q120 700 170 520 Q210 400 300 380 Z" fill="url(#body)"/>
 <path d="M330 420 Q500 395 670 420 Q690 520 660 560 L340 560 Q310 520 330 420 Z" fill="{shade(c, -.12)}"/>
 <rect x="440" y="430" width="120" height="70" rx="14" fill="#1d1d1f"/>
 <rect x="270" y="470" width="24" height="76" rx="6" fill="#1d1d1f"/><rect x="244" y="496" width="76" height="24" rx="6" fill="#1d1d1f"/>
 <circle cx="730" cy="470" r="16" fill="{acc}"/><circle cx="730" cy="546" r="16" fill="#1d1d1f"/><circle cx="692" cy="508" r="16" fill="#1d1d1f"/><circle cx="768" cy="508" r="16" fill="{acc}"/>
 <circle cx="410" cy="600" r="44" fill="#1d1d1f"/><circle cx="410" cy="600" r="30" fill="#2b2b2b"/>
 <circle cx="590" cy="600" r="44" fill="#1d1d1f"/><circle cx="590" cy="600" r="30" fill="#2b2b2b"/>
 <rect x="470" y="520" width="60" height="6" rx="3" fill="{acc}"/>
</g>"""


def gamepad(c):
    return floor(cy=800, rx=300) + gamepad_shape(c)


def handheld(c):
    return floor(rx=380) + f"""
<g filter="url(#soft)">
 <rect x="130" y="330" width="150" height="360" rx="70" fill="#ff6a00"/>
 <rect x="720" y="330" width="150" height="360" rx="70" fill="#2b2b2b"/>
 <rect x="270" y="330" width="460" height="360" rx="24" fill="#111"/>
 <rect x="292" y="352" width="416" height="316" rx="10" fill="url(#screen)"/>
 <rect x="292" y="352" width="416" height="316" rx="10" fill="url(#gloss)"/>
 <circle cx="205" cy="420" r="34" fill="#111"/><circle cx="795" cy="560" r="34" fill="#111"/>
 <circle cx="205" cy="560" r="12" fill="#111"/><circle cx="205" cy="610" r="12" fill="#111"/><circle cx="180" cy="585" r="12" fill="#111"/><circle cx="230" cy="585" r="12" fill="#111"/>
 <circle cx="795" cy="400" r="12" fill="#fff"/><circle cx="795" cy="450" r="12" fill="#fff"/><circle cx="770" cy="425" r="12" fill="#fff"/><circle cx="820" cy="425" r="12" fill="#fff"/>
</g>"""


def watch(c):
    return floor(rx=170) + f"""
<g filter="url(#soft)">
 <rect x="400" y="80" width="200" height="260" rx="40" fill="{shade(c, -.2)}"/>
 <rect x="400" y="660" width="200" height="260" rx="40" fill="{shade(c, -.2)}"/>
 <rect x="410" y="100" width="180" height="230" rx="34" fill="url(#bodyV)" opacity=".6"/>
 <rect x="330" y="290" width="340" height="410" rx="96" fill="url(#body)"/>
 <rect x="352" y="312" width="296" height="366" rx="78" fill="#050505"/>
 <circle cx="500" cy="495" r="120" fill="none" stroke="#ff6a00" stroke-width="22" stroke-dasharray="560 200" stroke-linecap="round" transform="rotate(-90 500 495)"/>
 <circle cx="500" cy="495" r="86" fill="none" stroke="#9aa0a6" stroke-width="18" stroke-dasharray="380 200" stroke-linecap="round" transform="rotate(-90 500 495)"/>
 <text x="500" y="512" fill="#fff" font-family="Poppins,Arial" font-weight="700" font-size="48" text-anchor="middle">10:09</text>
 <rect x="668" y="420" width="22" height="80" rx="10" fill="{shade(c, -.3)}"/>
 <rect x="330" y="290" width="340" height="410" rx="96" fill="url(#gloss)"/>
</g>"""


def watch_round(c):
    return floor(rx=170) + f"""
<g filter="url(#soft)">
 <rect x="410" y="80" width="180" height="260" rx="40" fill="{shade(c, -.25)}"/>
 <rect x="410" y="660" width="180" height="260" rx="40" fill="{shade(c, -.25)}"/>
 <circle cx="500" cy="500" r="200" fill="url(#body)"/>
 <circle cx="500" cy="500" r="172" fill="#050505"/>
 <circle cx="500" cy="500" r="130" fill="none" stroke="#ff6a00" stroke-width="18" stroke-dasharray="600 300" stroke-linecap="round" transform="rotate(-90 500 500)"/>
 <text x="500" y="518" fill="#fff" font-family="Poppins,Arial" font-weight="700" font-size="54" text-anchor="middle">08:15</text>
 <rect x="694" y="440" width="20" height="50" rx="8" fill="{shade(c, -.3)}"/><rect x="694" y="520" width="20" height="50" rx="8" fill="{shade(c, -.3)}"/>
</g>"""


def band(c):
    return floor(rx=200) + f"""
<g filter="url(#soft)">
 <path d="M500 140 Q760 160 760 500 Q760 840 500 860" fill="none" stroke="{shade(c, -.15)}" stroke-width="90" stroke-linecap="round"/>
 <path d="M500 140 Q240 160 240 500 Q240 840 500 860" fill="none" stroke="url(#body)" stroke-width="90" stroke-linecap="round"/>
 <rect x="410" y="300" width="180" height="400" rx="90" fill="#1d1d1f"/>
 <rect x="428" y="320" width="144" height="360" rx="72" fill="url(#screen)"/>
 <text x="500" y="470" fill="#fff" font-family="Poppins,Arial" font-weight="700" font-size="44" text-anchor="middle">7.842</text>
 <text x="500" y="510" fill="#fff" font-family="Inter,Arial" font-size="22" text-anchor="middle" opacity=".8">passi</text>
</g>"""


def speaker(c):
    grill = shade(c, -.25)
    return floor(rx=330) + f"""
<g filter="url(#soft)">
 <rect x="170" y="330" width="660" height="400" rx="200" fill="url(#bodyV)"/>
 <rect x="200" y="360" width="600" height="340" rx="170" fill="{grill}"/>
 {''.join(f'<circle cx="{230 + (i % 22) * 25.5}" cy="{385 + (i // 22) * 25}" r="5" fill="#000" opacity=".28"/>' for i in range(22 * 12))}
 <ellipse cx="170" cy="530" rx="48" ry="170" fill="#1d1d1f"/><ellipse cx="830" cy="530" rx="48" ry="170" fill="#1d1d1f"/>
 <ellipse cx="166" cy="530" rx="30" ry="120" fill="#2b2b2b"/><ellipse cx="834" cy="530" rx="30" ry="120" fill="#2b2b2b"/>
 <rect x="440" y="500" width="120" height="56" rx="16" fill="#fff" opacity=".92"/>
 <rect x="170" y="330" width="660" height="400" rx="200" fill="url(#gloss)"/>
</g>"""


def partybox(c):
    return floor(rx=270) + f"""
<g filter="url(#soft)">
 <rect x="240" y="150" width="520" height="700" rx="40" fill="url(#bodyV)"/>
 <rect x="440" y="120" width="120" height="50" rx="20" fill="#2b2b2b"/>
 <circle cx="500" cy="360" r="150" fill="#111"/><circle cx="500" cy="360" r="150" fill="none" stroke="#ff6a00" stroke-width="16"/>
 <circle cx="500" cy="360" r="70" fill="#2b2b2b"/>
 <circle cx="500" cy="660" r="150" fill="#111"/><circle cx="500" cy="660" r="150" fill="none" stroke="#ff8a3d" stroke-width="16"/>
 <circle cx="500" cy="660" r="70" fill="#2b2b2b"/>
 <circle cx="500" cy="360" r="190" fill="none" stroke="#ff6a00" stroke-width="4" opacity=".35"/>
</g>"""


def powerbank(c):
    return floor(rx=230) + f"""
<g filter="url(#soft)" transform="rotate(-12 500 500)">
 <rect x="330" y="170" width="340" height="640" rx="56" fill="url(#body)"/>
 <rect x="440" y="160" width="40" height="18" rx="6" fill="#111"/><rect x="520" y="160" width="40" height="18" rx="6" fill="#111"/>
 <rect x="380" y="560" width="240" height="110" rx="18" fill="#0b0b0c"/>
 <text x="500" y="636" fill="#ff6a00" font-family="Poppins,Arial" font-weight="700" font-size="60" text-anchor="middle">100%</text>
 {''.join(f'<rect x="{400 + i * 52}" y="700" width="36" height="12" rx="6" fill="#ff6a00"/>' for i in range(4))}
 <rect x="330" y="170" width="340" height="640" rx="56" fill="url(#gloss)"/>
</g>"""


def tablet(c):
    return floor(rx=330) + f"""
<g filter="url(#soft)">
 <rect x="170" y="190" width="660" height="620" rx="54" fill="{shade(c, -.25)}"/>
 <rect x="180" y="200" width="640" height="600" rx="46" fill="#0b0b0c"/>
 <rect x="206" y="226" width="588" height="548" rx="26" fill="url(#screen)"/>
 <rect x="250" y="290" width="200" height="24" rx="12" fill="#fff" opacity=".85"/>
 {ui_lines(250, 334, 180)}
 {''.join(f'<rect x="{250 + i * 130}" y="600" width="104" height="104" rx="24" fill="#fff" opacity=".18"/>' for i in range(4))}
 <rect x="206" y="226" width="588" height="548" rx="26" fill="url(#gloss)"/>
</g>"""


def monitor(c):
    return floor(cy=860, rx=260) + f"""
<g filter="url(#soft)">
 <path d="M120 200 Q500 160 880 200 L880 640 Q500 610 120 640 Z" fill="#0b0b0c"/>
 <path d="M140 220 Q500 182 860 220 L860 620 Q500 592 140 620 Z" fill="url(#screen)"/>
 <path d="M140 220 Q500 182 860 220 L860 620 Q500 592 140 620 Z" fill="url(#gloss)"/>
 <rect x="460" y="620" width="80" height="170" fill="{shade(c, .1)}"/>
 <path d="M330 830 Q500 790 670 830 L650 850 L350 850 Z" fill="{shade(c, .15)}"/>
 <rect x="200" y="300" width="230" height="26" rx="13" fill="#fff" opacity=".85"/>
 {ui_lines(200, 346, 200)}
</g>"""


def minipc(c):
    return floor(rx=300) + f"""
<g filter="url(#soft)">
 <path d="M200 520 L520 400 L800 480 L480 600 Z" fill="{shade(c, .25)}"/>
 <path d="M200 520 L480 600 L480 690 L200 610 Z" fill="url(#bodyV)"/>
 <path d="M480 600 L800 480 L800 570 L480 690 Z" fill="{shade(c, -.3)}"/>
 <circle cx="250" cy="580" r="10" fill="#ff6a00"/>
 {''.join(f'<rect x="{300 + i * 34}" y="{586 + i * 9}" width="20" height="10" rx="3" fill="#111" opacity=".6"/>' for i in range(4))}
 <path d="M380 470 L520 420 L640 455 L500 505 Z" fill="#fff" opacity=".08"/>
</g>"""


def charger(c):
    return floor(rx=200) + f"""
<g filter="url(#soft)">
 <rect x="360" y="300" width="280" height="380" rx="54" fill="url(#bodyV)"/>
 <rect x="390" y="230" width="22" height="90" rx="6" fill="#bfc3c8"/><rect x="588" y="230" width="22" height="90" rx="6" fill="#bfc3c8"/>
 <rect x="440" y="580" width="40" height="16" rx="7" fill="#111"/><rect x="520" y="580" width="40" height="16" rx="7" fill="#111"/>
 <rect x="460" y="620" width="80" height="22" rx="4" fill="#111"/>
 <text x="500" y="470" fill="#ff6a00" font-family="Poppins,Arial" font-weight="800" font-size="64" text-anchor="middle">65W</text>
 <path d="M500 690 Q500 790 640 820 Q760 840 800 760" fill="none" stroke="#e5e7eb" stroke-width="22" stroke-linecap="round"/>
</g>"""


def case(c):
    return floor(rx=200) + f"""
<g filter="url(#soft)" transform="rotate(8 500 500)">
 <rect x="330" y="130" width="340" height="720" rx="70" fill="url(#body)"/>
 <rect x="360" y="160" width="140" height="190" rx="40" fill="{shade(c, -.3)}"/>
 <circle cx="400" cy="210" r="28" fill="#111"/><circle cx="400" cy="300" r="28" fill="#111"/><circle cx="460" cy="255" r="22" fill="#111"/>
 <circle cx="500" cy="540" r="110" fill="none" stroke="{shade(c, -.2)}" stroke-width="10"/>
 <rect x="330" y="130" width="340" height="720" rx="70" fill="url(#gloss)"/>
</g>"""


def mouse(c):
    return floor(rx=200) + f"""
<g filter="url(#soft)">
 <path d="M500 170 Q700 180 700 480 Q700 830 500 840 Q300 830 300 480 Q300 180 500 170 Z" fill="url(#body)"/>
 <path d="M500 170 L500 420" stroke="{shade(c, -.4)}" stroke-width="6"/>
 <rect x="482" y="240" width="36" height="90" rx="18" fill="#1d1d1f"/>
 <rect x="490" y="256" width="20" height="58" rx="10" fill="#ff6a00"/>
 <path d="M300 520 Q240 560 260 640 Q300 600 320 560 Z" fill="{shade(c, -.25)}"/>
 <path d="M500 170 Q700 180 700 480 Q700 830 500 840 Q300 830 300 480 Q300 180 500 170 Z" fill="url(#gloss)"/>
</g>"""


def keyboard(c):
    keys = ""
    for r in range(5):
        for k in range(14):
            col = "#ff6a00" if (r == 0 and k == 0) or (r == 4 and 4 <= k <= 9) else "#2b2b2b"
            w = 38 if not (r == 4 and 4 <= k <= 9) else 38
            keys += f'<rect x="{168 + k * 48}" y="{392 + r * 48}" width="{w}" height="38" rx="7" fill="{col}"/>'
    return floor(rx=380) + f"""
<g filter="url(#soft)">
 <rect x="140" y="360" width="720" height="300" rx="28" fill="url(#bodyV)"/>
 {keys}
 <rect x="140" y="650" width="720" height="10" rx="5" fill="#ff6a00" opacity=".7"/>
</g>"""


RENDERS = {"phone": phone, "flip": flip, "laptop": laptop, "headphones": headphones, "headset": headset,
           "earbuds": earbuds, "console": console, "tower": tower, "gamepad": gamepad, "handheld": handheld,
           "watch": watch, "watch-round": watch_round, "band": band, "speaker": speaker, "partybox": partybox,
           "powerbank": powerbank, "tablet": tablet, "monitor": monitor, "minipc": minipc, "charger": charger,
           "case": case, "mouse": mouse, "keyboard": keyboard}


def page(svg_inner, color, bg=True, size=1000):
    background = """<rect width="1000" height="1000" fill="url(#bgG)"/><circle cx="500" cy="470" r="420" fill="url(#glow)"/>""" if bg else ""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;background:transparent}}svg{{display:block}}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 1000 1000">
{defs(color)}
<defs><linearGradient id="bgG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#eef0f3"/></linearGradient></defs>
{background}{svg_inner}</svg></body></html>"""


def shoot(job):
    html, png, size = job
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html); tmp = f.name
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                    f"--window-size={size},{size}", f"--screenshot={png}", f"file://{tmp}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    os.unlink(tmp)
    return png


def slug(s):
    return s.lower().replace(" ", "-")


def main():
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json")))
    os.makedirs(OUT_P, exist_ok=True); os.makedirs(OUT_C, exist_ok=True); os.makedirs(OUT_X, exist_ok=True)
    jobs = []
    for p in cat["products"]:
        fn = RENDERS[p["render"]]
        jobs.append((page(fn(p["color"]), p["color"]), f"{OUT_P}/{p['sku'].lower()}.png", 1000))
        jobs.append((page(fn(p["color"]), p["color"], bg=False), f"{OUT_X}/{p['sku'].lower()}.png", 1000))
        for name, col in p.get("variable", {}).get("Colore", {}).items():
            jobs.append((page(fn(col), col), f"{OUT_P}/{p['sku'].lower()}-{slug(name)}.png", 1000))
            jobs.append((page(fn(col), col, bg=False), f"{OUT_X}/{p['sku'].lower()}-{slug(name)}.png", 1000))
    for c in cat["categories"]:
        fn = RENDERS[c["render"]]
        jobs.append((page(fn(c["color"]), c["color"], bg=False, size=600), f"{OUT_C}/{c['slug']}.png", 600))
    only = os.environ.get("ONLY")
    if only:
        jobs = [j for j in jobs if only in j[1]]
    with cf.ThreadPoolExecutor(6) as ex:
        print(len(list(ex.map(shoot, jobs))), "images rendered")
    # Product photos: white background -> compressed JPG
    from PIL import Image
    for f in os.listdir(OUT_P):
        if f.endswith(".png"):
            src = os.path.join(OUT_P, f)
            Image.open(src).convert("RGB").save(src[:-4] + ".jpg", quality=86, optimize=True)
            os.remove(src)


if __name__ == "__main__":
    main()
