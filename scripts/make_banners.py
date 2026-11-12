#!/usr/bin/env python3
"""Generate PiShop logo, hero backgrounds and promo banners (HTML -> PNG via headless Chrome).

Usage: python3 -I scripts/make_banners.py <repo_root>
Output: assets/images/brand/*, assets/images/banners/*
Uses only the product renders produced by render_products.py (original artwork).
"""
import os, subprocess, sys, tempfile, concurrent.futures as cf

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
P = lambda sku: f"file://{ROOT}/assets/images/cutouts/{sku}.png"
BR = os.path.join(ROOT, "assets/images/brand"); BN = os.path.join(ROOT, "assets/images/banners")

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;600&display=swap" rel="stylesheet">'
BASE = """*{box-sizing:border-box;margin:0;padding:0}html,body{width:%dpx;height:%dpx;overflow:hidden;background:transparent;font-family:Poppins,Arial,sans-serif}
.b{position:relative;width:100%%;height:100%%;overflow:hidden;border-radius:0}
.img{position:absolute;filter:drop-shadow(0 30px 40px rgba(0,0,0,.35))}
.tag{display:inline-block;padding:8px 18px;border-radius:999px;font-weight:700;font-size:18px;letter-spacing:.5px}
h1,h2{font-weight:800;line-height:1.02;letter-spacing:-1px}
.btn{display:inline-block;margin-top:22px;padding:14px 28px;border-radius:999px;font-weight:700;font-size:18px}
"""

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 96" width="330" height="96">
 <rect x="0" y="8" width="80" height="80" rx="22" fill="#FF6A00"/>
 <path d="M18 34 Q18 26 26 26 L62 26" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <path d="M32 27 L30 70" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <path d="M50 27 Q48 52 52 64 Q55 72 63 68" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <text x="96" y="68" font-family="Poppins,Arial,sans-serif" font-weight="800" font-size="54" fill="{fg}" letter-spacing="-1">Pi<tspan fill="#FF6A00">Shop</tspan></text>
</svg>"""

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="512" height="512">
 <rect x="0" y="0" width="80" height="80" rx="20" fill="#FF6A00"/>
 <path d="M18 28 Q18 20 26 20 L62 20" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <path d="M32 21 L30 64" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <path d="M50 21 Q48 46 52 58 Q55 66 63 62" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
</svg>"""


def html(w, h, body, extra_css=""):
    return f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{BASE % (w, h)}{extra_css}</style></head><body>{body}</body></html>"


JOBS = []


def add(name, w, h, body, css="", folder=BN):
    JOBS.append((html(w, h, body, css), os.path.join(folder, name), w, h))


# ── Brand ─────────────────────────────────────────────────────────────
def brand():
    os.makedirs(BR, exist_ok=True)
    open(f"{BR}/logo.svg", "w").write(LOGO_SVG.replace("{fg}", "#111111"))
    open(f"{BR}/logo-white.svg", "w").write(LOGO_SVG.replace("{fg}", "#FFFFFF"))
    open(f"{BR}/icon.svg", "w").write(ICON_SVG)
    add("logo.png", 660, 192, f"<div style='transform:scale(2);transform-origin:0 0'>{LOGO_SVG.replace('{fg}', '#111111')}</div>", folder=BR)
    add("logo-white.png", 660, 192, f"<div style='transform:scale(2);transform-origin:0 0'>{LOGO_SVG.replace('{fg}', '#FFFFFF')}</div>", folder=BR)
    add("icon.png", 512, 512, ICON_SVG, folder=BR)
    # Testimonial avatars (initials, no real people's photos)
    for k, (ini, bg, fg) in enumerate([("GR", "#FF6A00", "#FFFFFF"), ("MB", "#111111", "#FF6A00"), ("FL", "#FFF1E6", "#FF6A00")]):
        add(f"avatar-{k}.png", 200, 200, f"<div style='width:200px;height:200px;border-radius:50%;background:{bg};color:{fg};display:grid;place-items:center;font:800 76px Poppins'>{ini}</div>", folder=BR)


# ── Hero backgrounds (no text: copy lives in Elementor) ──────────────
def heroes():
    bg_dark = "background:radial-gradient(circle at 75% 45%,#3a2010 0,#151515 45%,#0b0b0b 100%)"
    add("hero-smartphone.png", 1600, 640, f"""<div class='b' style='{bg_dark}'>
      <div style='position:absolute;right:40px;top:40px;width:560px;height:560px;border-radius:50%;background:radial-gradient(circle,#ff6a00 0,rgba(255,106,0,.0) 70%);opacity:.55'></div>
      <img class='img' src='{P("pi-sp-002")}' style='right:330px;top:110px;width:400px;transform:rotate(-6deg)'>
      <img class='img' src='{P("pi-sp-001-arancione")}' style='right:20px;top:40px;width:540px'>
    </div>""")
    add("hero-laptop.png", 1600, 640, f"""<div class='b' style='background:linear-gradient(120deg,#ff6a00 0,#ff8a3d 45%,#ffb27a 100%)'>
      <div style='position:absolute;right:-120px;top:-200px;width:900px;height:900px;border-radius:50%;background:rgba(255,255,255,.12)'></div>
      <img class='img' src='{P("pi-lp-001")}' style='right:120px;top:80px;width:480px'>
      <img class='img' src='{P("pi-au-001")}' style='right:-20px;top:250px;width:330px'>
    </div>""")
    add("hero-gaming.png", 1600, 640, f"""<div class='b' style='background:linear-gradient(135deg,#111 0,#2b2b2b 60%,#3a3a3c 100%)'>
      <div style='position:absolute;left:0;right:0;bottom:0;height:40%;background:linear-gradient(0deg,rgba(255,106,0,.35),transparent)'></div>
      <img class='img' src='{P("pi-gm-001")}' style='right:200px;top:50px;width:460px'>
      <img class='img' src='{P("pi-gm-003-arancione")}' style='right:0px;top:250px;width:380px'>
      <img class='img' src='{P("pi-gm-005")}' style='right:560px;top:320px;width:220px;opacity:.95'>
    </div>""")


# ── Promo banners (text baked in, like the reference banners) ────────
def promo(name, w, h, bg, fg, tag_bg, tag_fg, tag, title, sub, cta, cta_bg, cta_fg, imgs):
    imgs_html = "".join(f"<img class='img' src='{P(s)}' style='{st}'>" for s, st in imgs)
    add(name, w, h, f"""<div class='b' style='background:{bg};color:{fg}'>
      <div style='position:absolute;left:{int(w * .06)}px;top:50%;transform:translateY(-50%);max-width:{int(w * (.42 if w > 1000 else .5))}px;z-index:2'>
        <span class='tag' style='background:{tag_bg};color:{tag_fg}'>{tag}</span>
        <h2 style='font-size:{int(h * .14)}px;margin-top:14px'>{title}</h2>
        <p style='font-family:Inter;font-size:{max(16, int(h * .055))}px;margin-top:10px;opacity:.85'>{sub}</p>
        <span class='btn' style='background:{cta_bg};color:{cta_fg}'>{cta} →</span>
      </div>{imgs_html}</div>""")


def banners():
    os.makedirs(BN, exist_ok=True)
    promo("promo-audio.png", 800, 420, "linear-gradient(135deg,#111,#2b2b2b)", "#fff", "#ff6a00", "#fff", "AUDIO",
          "Cuffie<br>fino al -30%", "Cancellazione del rumore top di gamma", "Scopri", "#fff", "#111",
          [("pi-au-003", "right:-20px;top:40px;width:400px")])
    promo("promo-smartwatch.png", 800, 420, "linear-gradient(135deg,#ff6a00,#ff8a3d)", "#fff", "#111", "#fff", "NOVITÀ",
          "Smartwatch<br>per ogni sport", "Salute e notifiche al polso", "Acquista", "#111", "#fff",
          [("pi-sw-001", "right:10px;top:20px;width:380px")])
    promo("promo-powerbank.png", 800, 420, "linear-gradient(135deg,#f4f5f7,#e5e7eb)", "#111", "#ff6a00", "#fff", "DA 29,99 €",
          "Energia<br>sempre con te", "Power bank e caricatori GaN", "Vedi tutti", "#ff6a00", "#fff",
          [("pi-pb-001", "right:120px;top:30px;width:330px"), ("pi-ac-001", "right:-30px;top:120px;width:300px")])
    promo("promo-laptop.png", 800, 420, "linear-gradient(135deg,#e5e7eb,#f4f5f7)", "#111", "#111", "#fff", "LAPTOP",
          "MacBook Air M4<br>da 1.349 €", "Leggero, silenzioso, potente", "Scopri", "#ff6a00", "#fff",
          [("pi-lp-001", "right:-30px;top:60px;width:430px")])
    promo("promo-tablet.png", 800, 420, "linear-gradient(135deg,#2b2b2b,#111)", "#fff", "#ff6a00", "#fff", "TABLET",
          "Studio e svago<br>in un tablet", "iPad Air M2 e Galaxy Tab S10 FE", "Acquista", "#fff", "#111",
          [("pi-tb-002", "right:-10px;top:50px;width:380px")])
    promo("banner-gamer-bundle.png", 1600, 520, "radial-gradient(circle at 70% 50%,#3a2010 0,#111 55%)", "#fff", "#ff6a00", "#fff",
          "PACCHETTO GAMER", "Console + controller<br>risparmi 90 €", "PS5 Slim, DualSense extra e cuffie PULSE Elite in un unico pacchetto.",
          "Componi il tuo pacchetto", "#ff6a00", "#fff",
          [("pi-gm-001", "right:330px;top:-10px;width:520px"), ("pi-gm-003-nero", "right:170px;top:210px;width:340px"),
           ("pi-gm-005", "right:-20px;top:60px;width:340px")])
    promo("banner-sale-50.png", 1600, 420, "linear-gradient(100deg,#ff6a00 0,#ff6a00 55%,#111 55%)", "#fff", "#111", "#fff",
          "SALDI TECH", "Fino al -50%", "Su una selezione di laptop, monitor e accessori. Fino a esaurimento scorte.",
          "Approfitta ora", "#111", "#fff",
          [("pi-pc-001", "right:380px;top:10px;width:420px"), ("pi-lp-003", "right:20px;top:40px;width:420px")])
    promo("banner-shipping.png", 1600, 300, "linear-gradient(90deg,#111,#2b2b2b)", "#fff", "#ff6a00", "#fff",
          "SPEDIZIONE GRATUITA", "Sopra i 49 € in tutta Italia", "Consegna in 24/48 ore con corriere espresso e reso gratuito entro 14 giorni.",
          "Info spedizioni", "#fff", "#111",
          [("pi-sk-001", "right:60px;top:-10px;width:330px")])
    # Offerte lampo header art
    add("flash-deals.png", 1600, 420, f"""<div class='b' style='background:linear-gradient(120deg,#111 0,#2b2b2b 50%,#ff6a00 50%,#ff8a3d 100%)'>
      <img class='img' src='{P("pi-sp-003")}' style='left:660px;top:-10px;width:420px'>
      <img class='img' src='{P("pi-sk-001")}' style='right:40px;top:40px;width:400px'>
      <img class='img' src='{P("pi-sw-002")}' style='left:960px;top:150px;width:300px'>
    </div>""")
    # Category hero for blog / about
    add("about-hero.png", 1600, 520, f"""<div class='b' style='background:linear-gradient(135deg,#f4f5f7,#ffffff)'>
      <div style='position:absolute;right:-100px;top:-160px;width:760px;height:760px;border-radius:50%;background:#FFF1E6'></div>
      <img class='img' src='{P("pi-tb-001")}' style='right:520px;top:80px;width:400px'>
      <img class='img' src='{P("pi-lp-002")}' style='right:160px;top:60px;width:480px'>
      <img class='img' src='{P("pi-sp-005")}' style='right:20px;top:170px;width:300px'>
    </div>""")


def shoot(job):
    doc, png, w, h = job
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(doc); tmp = f.name
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--default-background-color=00000000", "--virtual-time-budget=4000",
                    f"--window-size={w},{h}", f"--screenshot={png}", f"file://{tmp}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    os.unlink(tmp)
    return png


if __name__ == "__main__":
    brand(); heroes(); banners()
    with cf.ThreadPoolExecutor(6) as ex:
        print(len(list(ex.map(shoot, JOBS))), "images rendered")
