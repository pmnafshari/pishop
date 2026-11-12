#!/usr/bin/env python3
"""Build Elementor page data for PiShop.

Usage: python3 -I scripts/build_pages.py <repo_root>
Reads : data/media-map.json, data/catalog.json, data/legal.json
Writes: data/build/site.json  ({templates:[...], pages:[...]}) consumed by scripts/apply-pages.php

Every page is a normal Elementor document (containers + core widgets), fully editable
in the Elementor editor. Colours reference Elementor *Global Colors* (set in the kit).
"""
import hashlib, json, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
MEDIA = json.load(open(f"{ROOT}/data/media-map.json"))
CAT = json.load(open(f"{ROOT}/data/catalog.json"))
LEGAL = json.load(open(f"{ROOT}/data/legal.json"))

# ── ids ────────────────────────────────────────────────────────────────
_ctx = {"page": "x", "n": 0}


def uid():
    _ctx["n"] += 1
    return hashlib.md5(f"{_ctx['page']}-{_ctx['n']}".encode()).hexdigest()[:7]


# ── global colours (ids defined in apply-pages.php kit) ───────────────
G = {"orange": "primary", "black": "secondary", "text": "text", "gray": "accent",
     "white": "pi_white", "g100": "pi_gray100", "g200": "pi_gray200", "olight": "pi_orange_light", "odark": "pi_orange_dark"}
HEX = {"orange": "#FF6A00", "black": "#111111", "text": "#2B2B2B", "gray": "#6B7280", "white": "#FFFFFF",
       "g100": "#F4F5F7", "g200": "#E5E7EB", "olight": "#FFF1E6", "odark": "#E05A00"}


def gcol(settings, key, name):
    """Set a colour both as value (fallback) and as a global reference."""
    if not name:
        return
    settings[key] = HEX[name]
    settings.setdefault("__globals__", {})[key] = f"globals/colors?id={G[name]}"


def m(key):
    v = MEDIA[key]
    return {"id": v["id"], "url": v["url"]}


def box(t=0, r=0, b=0, l=0, unit="px"):
    return {"unit": unit, "top": str(t), "right": str(r), "bottom": str(b), "left": str(l), "isLinked": False}


def size(v, unit="px"):
    return {"unit": unit, "size": v, "sizes": []}


def radius(v):
    return {"unit": "px", "top": str(v), "right": str(v), "bottom": str(v), "left": str(v), "isLinked": True}


def typo(s, prefix, family=None, sz=None, weight=None, lh=None, sz_m=None, ls=None, transform=None):
    s[f"{prefix}_typography"] = "custom"
    if family: s[f"{prefix}_font_family"] = family
    if sz: s[f"{prefix}_font_size"] = size(sz)
    if sz_m: s[f"{prefix}_font_size_mobile"] = size(sz_m)
    if weight: s[f"{prefix}_font_weight"] = str(weight)
    if lh: s[f"{prefix}_line_height"] = size(lh, "em")
    if ls is not None: s[f"{prefix}_letter_spacing"] = size(ls)
    if transform: s[f"{prefix}_text_transform"] = transform


# ── elements ──────────────────────────────────────────────────────────
def C(*children, dir="column", width=None, width_t=None, width_m=None, boxed=False, bw=1280, gap=20, pad=None, pad_m=None,
      bg=None, bg_img=None, slideshow=None, overlay=None, rad=None, minh=None, minh_m=None, justify=None, align=None,
      wrap=False, cls="", dir_m=None, dir_t=None, margin=None, border=None, link=None, tag=None, title=None, overflow=False, **extra):
    s = {"content_width": "boxed" if boxed else "full", "flex_direction": dir,
         "flex_gap": {"column": str(gap), "row": str(gap), "isLinked": True, "unit": "px", "size": gap}}
    if boxed: s["boxed_width"] = size(bw)
    if width is not None: s["width"] = size(width, "%")
    if width_t is not None: s["width_tablet"] = size(width_t, "%")
    if width_m is not None: s["width_mobile"] = size(width_m, "%")
    if pad is not None: s["padding"] = box(*pad)
    if pad_m is not None: s["padding_mobile"] = box(*pad_m)
    if margin is not None: s["margin"] = box(*margin)
    if bg: s["background_background"] = "classic"; gcol(s, "background_color", bg)
    if bg_img:
        s["background_background"] = "classic"; s["background_image"] = m(bg_img)
        s.update({"background_position": "center center", "background_size": "cover", "background_repeat": "no-repeat"})
    if slideshow:
        s["background_background"] = "slideshow"
        s["background_slideshow_gallery"] = [m(k) for k in slideshow]
        s.update({"background_slideshow_loop": "yes", "background_slideshow_slide_duration": 5000,
                  "background_slideshow_slide_transition": "fade", "background_slideshow_transition_duration": 900,
                  "background_slideshow_background_size": "cover", "background_slideshow_background_position": "center right",
                  "background_slideshow_ken_burns": "yes", "background_slideshow_ken_burns_zoom_direction": "in"})
    if overlay:
        s["background_overlay_background"] = "gradient"
        s["background_overlay_color"] = overlay[0]; s["background_overlay_color_b"] = overlay[1]
        s["background_overlay_gradient_angle"] = size(90, "deg")
        s["background_overlay_color_stop"] = size(overlay[2] if len(overlay) > 2 else 0, "%")
        s["background_overlay_color_b_stop"] = size(100, "%")
    if rad: s["border_radius"] = radius(rad)
    if minh: s["min_height"] = size(minh)
    if minh_m: s["min_height_mobile"] = size(minh_m)
    if justify: s["flex_justify_content"] = justify
    if align: s["flex_align_items"] = align
    if wrap == "m":  # one line on desktop, wrap on tablet/mobile
        s["flex_wrap"] = "nowrap"; s["flex_wrap_tablet"] = "wrap"; s["flex_wrap_mobile"] = "wrap"
    elif wrap: s["flex_wrap"] = "wrap"
    if dir_m: s["flex_direction_mobile"] = dir_m
    if dir_t: s["flex_direction_tablet"] = dir_t
    if cls: s["css_classes"] = cls
    if border:
        s["border_border"] = "solid"; s["border_width"] = box(*border[0]); gcol(s, "border_color", border[1])
    if link: s["html_tag"] = "a"; s["link"] = {"url": link, "is_external": "", "nofollow": ""}
    if tag: s["html_tag"] = tag
    if title: s["_title"] = title
    if overflow: s["overflow"] = "hidden"
    s.update(extra)
    return {"id": uid(), "elType": "container", "isInner": False, "settings": s, "elements": list(children)}


def W(wtype, **s):
    return {"id": uid(), "elType": "widget", "widgetType": wtype, "isInner": False, "settings": s, "elements": []}


def H(text, tag="h2", sz=32, color="black", align=None, weight=700, sz_m=None, link=None, cls="", lh=1.15, mb=None):
    s = {"title": text, "header_size": tag}
    gcol(s, "title_color", color)
    typo(s, "typography", "Poppins", sz, weight, lh, sz_m or (round(sz * .72) if sz > 24 else None))
    if align: s["align"] = align; s["align_mobile"] = align
    if link: s["link"] = {"url": link}
    if cls: s["_css_classes"] = cls
    if mb is not None: s["_margin"] = box(0, 0, mb, 0)
    return W("heading", **s)


def T(html, color="text", sz=16, align=None, cls="", lh=1.6, mb=None):
    s = {"editor": html}
    gcol(s, "text_color", color)
    typo(s, "typography", "Inter", sz, 400, lh)
    if align: s["align"] = align
    if cls: s["_css_classes"] = cls
    if mb is not None: s["_margin"] = box(0, 0, mb, 0)
    return W("text-editor", **s)


def BTN(text, url, style="orange", align=None, icon=True, sz=15, full_m=False):
    s = {"text": text, "link": {"url": url, "is_external": "", "nofollow": ""}, "size": "md",
         "border_radius": radius(999), "text_padding": box(14, 26, 14, 26)}
    typo(s, "typography", "Poppins", sz, 600)
    styles = {"orange": ("orange", "white", "black", "white"), "dark": ("black", "white", "orange", "white"),
              "white": ("white", "black", "orange", "white"), "ghost": (None, "white", "white", "black"),
              "outline": (None, "black", "black", "white")}
    bgc, fg, hbg, hfg = styles[style]
    if bgc: gcol(s, "background_color", bgc)
    else:
        s["background_color"] = "rgba(0,0,0,0)"
        s["border_border"] = "solid"; s["border_width"] = box(2, 2, 2, 2); gcol(s, "border_color", fg)
    gcol(s, "button_text_color", fg); gcol(s, "button_background_hover_color", hbg); gcol(s, "hover_color", hfg)
    if icon:
        s["selected_icon"] = {"value": "fas fa-arrow-right", "library": "fa-solid"}; s["icon_align"] = "right"
        s["icon_indent"] = size(8)
    if align: s["align"] = align
    if full_m: s["align_mobile"] = "justify"
    return W("button", **s)


def IMG(key, link=None, rad=16, width=None, cls="pi-hover-lift", alt=None):
    s = {"image": m(key), "image_size": "full", "image_border_radius": radius(rad)}
    if link: s["link_to"] = "custom"; s["link"] = {"url": link}
    if width: s["width"] = size(width, "%")
    if cls: s["_css_classes"] = cls
    return W("image", **s)


def SC(code, cls=""):
    s = {"shortcode": code}
    if cls: s["_css_classes"] = cls
    return W("shortcode", **s)


def ICONBOX(icon, title, desc, pos="left", color="orange", title_color="black", desc_color="gray", view="stacked", lib="fa-solid"):
    s = {"selected_icon": {"value": icon, "library": lib}, "title_text": title, "description_text": desc,
         "position": pos, "view": view, "shape": "circle", "title_size": "h4", "icon_size": size(22), "icon_padding": size(14),
         "icon_space": size(14)}
    if view == "stacked":
        gcol(s, "primary_color", "olight"); gcol(s, "secondary_color", color)
    else:
        gcol(s, "primary_color", color)
    gcol(s, "title_color", title_color); gcol(s, "description_color", desc_color)
    typo(s, "title_typography", "Poppins", 16, 700, 1.3)
    typo(s, "description_typography", "Inter", 14, 400, 1.5)
    if pos == "top": s["text_align"] = "center"
    return W("icon-box", **s)


def ICONLIST(items, color="white", icon_color="orange", inline=False, sz=14, hover="orange", space=10):
    lst = []
    for it in items:
        text, url = it[0], it[1]
        icon = it[2] if len(it) > 2 else "fas fa-angle-right"
        lst.append({"_id": uid(), "text": text, "selected_icon": {"value": icon, "library": "fa-brands" if icon.startswith("fab") else "fa-solid"},
                    "link": {"url": url or "", "is_external": "", "nofollow": ""}})
    s = {"icon_list": lst, "space_between": size(space), "icon_size": size(12)}
    if inline: s["view"] = "inline"
    gcol(s, "icon_color", icon_color); gcol(s, "text_color", color); gcol(s, "text_color_hover", hover)
    typo(s, "icon_typography", "Inter", sz, 400, 1.4)
    return W("icon-list", **s)


def SPACER(h):
    return W("spacer", space=size(h))


def section_head(eyebrow, title, link_text=None, link=None, color="black", center=False):
    left = C(*([SC(f'<span class="pi-eyebrow">{eyebrow}</span>')] if eyebrow else []), H(title, "h2", 30, color, "center" if center else None),
             gap=6, width=None if center else 70, width_m=100, align="center" if center else None)
    items = [left]
    if link and not center:
        items.append(C(BTN(link_text, link, "outline", "right", sz=14), width=30, width_m=100, justify="flex-end", align="flex-end"))
    return C(*items, dir="row", dir_m="column", justify="space-between" if not center else "center", align="flex-end",
             gap=10, margin=(0, 0, 18, 0))


def page_hero(title, subtitle, img="banners/about-hero", dark=False, crumbs=None):
    color = "white" if dark else "black"
    inner = [T(f'<a href="/">Home</a> / {crumbs or title}', "gray" if not dark else "g200", 13, mb=0),
             H(title, "h1", 46, color, sz_m=32), T(subtitle, "gray" if not dark else "g200", 17)]
    return C(C(*inner, width=48, width_t=70, width_m=100, gap=8), boxed=True, pad=(70, 20, 70, 20), pad_m=(40, 16, 40, 16), bg_img=img, minh=320,
             minh_m=0, justify="center", dir="column", cls="pi-page-hero",
             overlay=("rgba(255,255,255,0.97)", "rgba(255,255,255,0)", 48) if not dark else ("rgba(17,17,17,0.92)", "rgba(17,17,17,0.15)", 40),
             background_position="center right")


# ══════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════
def header():
    _ctx.update(page="header", n=0)
    topbar = C(
        C(T("🚚 Spedizione gratuita sopra 49 €<span class=\"pi-tb-more\"> &nbsp;·&nbsp; ↩️ Reso gratuito entro 14 giorni &nbsp;·&nbsp; 💳 Paga anche alla consegna</span>", "white", 13, lh=1.3),
          width=65, width_m=100),
        C(ICONLIST([("Traccia ordine", "/traccia-ordine/", "fas fa-truck"), ("Assistenza", "/contatti/", "fas fa-headset"),
                    ("Offerte Lampo", "/offerte-lampo/", "fas fa-bolt")], "white", "orange", inline=True, sz=13),
          width=35, width_m=100, justify="center", align="flex-end", cls="elementor-hidden-mobile"),
        dir="row", boxed=True, pad=(9, 20, 9, 20), bg="black", align="center", justify="space-between", gap=10, cls="pi-topbar")
    main = C(
        C(W("image", image=m("brand/logo"), image_size="full", width=size(170, "px"), width_mobile=size(130, "px"), align="left",
            link_to="custom", link={"url": "/"}, _css_classes="pi-logo"), width=18, width_t=25, width_m=45, cls="pi-hm-logo"),
        C(SC("[pishop_search]"), width=50, width_t=40, width_m=100, cls="pi-hm-search"),
        C(SC("[pishop_header_icons]"), width=28, width_t=35, width_m=50, align="flex-end", cls="pi-hm-icons"),
        dir="row", wrap=True, boxed=True, pad=(16, 20, 16, 20), pad_m=(12, 16, 12, 16), bg="white", align="center",
        justify="space-between", gap=16, cls="pi-header-main")
    nav = C(
        C(W("navigation-menu", menu="menu-principale", layout="horizontal", align_items="left", pointer="underline",
            dropdown="tablet", submenu_icon="arrow", full_width="yes", toggle_align="left",
            **{"__globals__": {"color_menu_item": f"globals/colors?id={G['black']}", "color_menu_item_hover": f"globals/colors?id={G['orange']}",
                               "pointer_color_menu_item_hover": f"globals/colors?id={G['orange']}", "color_dropdown_item": f"globals/colors?id={G['black']}"}},
            color_menu_item=HEX["black"], color_menu_item_hover=HEX["orange"], pointer_color_menu_item_hover=HEX["orange"],
            padding_horizontal_menu_item=size(14), padding_vertical_menu_item=size(12), _css_classes="pi-nav"),
          width=75, width_m=50),
        C(ICONLIST([("02 1234 5678", "tel:+390212345678", "fas fa-phone-alt")], "black", "orange", inline=True, sz=14),
          width=25, width_m=50, align="flex-end", justify="center"),
        dir="row", dir_m="row", boxed=True, pad=(2, 20, 2, 20), bg="white", align="center", justify="space-between",
        border=((1, 0, 1, 0), "g200"), cls="pi-header-nav")
    return [topbar, main, nav]


# ══════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════
def footer():
    _ctx.update(page="footer", n=0)
    benefits = C(*[C(ICONBOX(i, t, d), width=23, width_t=47, width_m=100) for i, t, d in [
        ("fas fa-shipping-fast", "Spedizione gratuita", "Su tutti gli ordini sopra 49 € in Italia"),
        ("fas fa-undo-alt", "Reso entro 14 giorni", "Reso semplice e gratuito, senza domande"),
        ("fas fa-shield-alt", "Pagamenti sicuri", "Carta, bonifico o contrassegno"),
        ("fas fa-headset", "Assistenza 7 giorni su 7", "Esperti a tua disposizione via chat e telefono")]],
        dir="row", wrap="m", justify="space-between", boxed=True, pad=(36, 20, 36, 20), bg="g100", gap=20)
    newsletter = C(
        C(H("Iscriviti alla newsletter", "h3", 28, "white", sz_m=22),
          T("Ricevi in anteprima offerte lampo e novità. Subito per te un coupon di 10 € sul primo ordine.", "white", 15), width=50, width_m=100, gap=4),
        C(SC("[wpforms id=\"{{FORM_NEWSLETTER}}\" title=\"false\"]", cls="pi-newsletter"), width=50, width_m=100),
        dir="row", dir_m="column", boxed=True, pad=(34, 20, 34, 20), bg="orange", align="center", gap=24)
    col = lambda title, items: C(H(title, "h4", 16, "white", mb=6), ICONLIST(items, "g200", "orange", sz=14, space=8), width=15, width_t=30, width_m=100, gap=10)
    cats = [(c["name"], f"/categoria-prodotto/{c['slug']}/") for c in CAT["categories"][:7]]
    main = C(
        C(W("image", image=m("brand/logo-white"), image_size="full", width=size(170, "px"), align="left", link_to="custom", link={"url": "/"}),
          T("PiShop è il negozio online di elettronica con sede a Milano. Smartphone, laptop, gaming e accessori originali con garanzia Italia.", "g200", 14),
          W("social-icons", social_icon_list=[{"_id": uid(), "social_icon": {"value": v, "library": "fa-brands"}, "link": {"url": u, "is_external": "on"}}
                                              for v, u in [("fab fa-instagram", "https://instagram.com/"), ("fab fa-facebook-f", "https://facebook.com/"),
                                                           ("fab fa-tiktok", "https://tiktok.com/"), ("fab fa-youtube", "https://youtube.com/"),
                                                           ("fab fa-whatsapp", "https://wa.me/390212345678")]],
            shape="circle", icon_color="custom", icon_primary_color="#2B2B2B", icon_secondary_color="#FFFFFF", icon_size=size(15),
            icon_padding=size(.7, "em"), icon_spacing=size(8), hover_primary_color=HEX["orange"], align="left"),
          width=26, width_t=100, width_m=100, gap=14),
        col("Negozio", cats),
        col("Assistenza", [("Il mio account", "/mio-account/"), ("Traccia ordine", "/traccia-ordine/"), ("Spedizioni e resi", "/spedizioni-e-resi/"),
                           ("Domande frequenti", "/faq/"), ("Contatti", "/contatti/")]),
        col("Informazioni", [("Chi siamo", "/chi-siamo/"), ("Blog", "/blog/"), ("Marchi", "/marchi/"), ("Termini e condizioni", "/termini-e-condizioni/"),
                             ("Privacy Policy", "/privacy-policy/"), ("Cookie Policy", "/cookie-policy/")]),
        C(H("Contatti", "h4", 16, "white", mb=6),
          ICONLIST([("Via Torino 21, 20123 Milano", "https://maps.google.com/?q=Via+Torino+21+Milano", "fas fa-map-marker-alt"),
                    ("02 1234 5678", "tel:+390212345678", "fas fa-phone-alt"), ("assistenza@pishop.example", "mailto:assistenza@pishop.example", "fas fa-envelope"),
                    ("Lun–Sab 9:00–19:00", "", "fas fa-clock")], "g200", "orange", sz=14, space=8), width=18, width_t=30, width_m=100, gap=10),
        dir="row", wrap=True, justify="space-between", boxed=True, pad=(56, 20, 40, 20), bg="black", gap=24, cls="pi-footer")
    bottom = C(
        C(T("© [pishop_year] PiShop S.r.l. · P.IVA 01234567890 · Tutti i diritti riservati. Sito dimostrativo.", "gray", 13), width=58, width_m=100),
        C(SC('<div class="pi-pay"><span>VISA</span><span>Mastercard</span><span>PayPal</span><span>Bonifico</span><span>Contrassegno</span></div>'),
          width=38, width_m=100, align="flex-end"),
        dir="row", dir_m="column", wrap=True, boxed=True, pad=(18, 20, 18, 20), bg="black", align="center", justify="space-between",
        border=((1, 0, 0, 0), "text"), cls="pi-footer")
    return [benefits, newsletter, main, bottom]


# ══════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════
def home():
    _ctx.update(page="home", n=0)
    hero = C(
        C(SC('<span class="pi-eyebrow" style="background:#ff6a00;color:#fff">Nuova collezione 2026</span>'),
          H("La tecnologia<br>che ami, al<br>prezzo giusto.", "h1", 50, "white", sz_m=32, lh=1.05),
          T("Smartphone, laptop e gaming dei migliori marchi.<br>Spedizione gratuita sopra 49 € e reso entro 14 giorni.", "g200", 17),
          C(BTN("Scopri il negozio", "/negozio/", "orange"), BTN("Offerte lampo", "/offerte-lampo/", "ghost", icon=False),
            dir="row", wrap=True, gap=12, margin=(10, 0, 0, 0)),
          width=66, width_t=100, width_m=100, slideshow=["banners/hero-smartphone", "banners/hero-laptop", "banners/hero-gaming"],
          overlay=("rgba(17,17,17,0.92)", "rgba(17,17,17,0)", 38), rad=22, minh=470, minh_m=420, pad=(50, 48, 50, 48), pad_m=(32, 22, 32, 22),
          justify="center", gap=14, overflow=True, cls="pi-hero"),
        C(IMG("banners/promo-smartwatch", "/categoria-prodotto/smartwatch/", 22), IMG("banners/promo-powerbank", "/categoria-prodotto/power-bank/", 22),
          width=34, width_t=100, width_m=100, dir_t="row", dir_m="column", gap=16, justify="space-between"),
        dir="row", dir_t="column", boxed=True, pad=(24, 20, 24, 20), gap=16)

    tiles = [C(W("image-box", image=m(f"categories/{c['slug']}"), title_text=c["name"], description_text="", link={"url": f"/categoria-prodotto/{c['slug']}/"},
                 position="top", image_size=size(78, "%"), title_size="h3", text_align="center", _css_classes="pi-cat-tile",
                 title_typography_typography="custom", title_typography_font_family="Poppins", title_typography_font_size=size(15),
                 title_typography_font_weight="600", image_space=size(10)),
               width=10, width_t=20, width_m=33) for c in CAT["categories"]]
    cats = C(section_head("Categorie", "Esplora le categorie", "Tutti i prodotti", "/negozio/"),
             C(*tiles, dir="row", wrap=True, gap=0, justify="space-between"), boxed=True, pad=(36, 20, 20, 20), gap=0)

    flash = C(
        C(C(H("⚡ Offerte Lampo", "h2", 34, "white", sz_m=26), T("Prezzi imbattibili per poche ore. Quando finiscono, finiscono!", "g200", 15),
            width=45, width_m=100, gap=4),
          C(SC("[pishop_countdown]"), width=55, width_m=100, align="flex-end", cls="pi-cd-wrap"),
          dir="row", dir_m="column", align="center", justify="space-between", gap=14),
        SC("[pishop_flash_products columns=\"4\" limit=\"4\"]"),
        C(BTN("Vedi tutte le offerte", "/offerte-lampo/", "orange", "center"), align="center"),
        boxed=True, pad=(40, 36, 40, 36), pad_m=(28, 14, 28, 14), bg="black", rad=24, gap=24, margin=(20, 0, 20, 0), cls="pi-flash-box pi-dark")
    flash_wrap = C(flash, boxed=True, pad=(0, 20, 0, 20))

    new = C(section_head("Novità", "Nuovi arrivi", "Vedi tutti", "/tag-prodotto/novita/"),
            SC('[products tag="novita" limit="8" columns="4" orderby="menu_order"]'), boxed=True, pad=(36, 20, 20, 20), gap=0)

    promos = C(*[C(IMG(f"banners/{b}", u, 20), width=33.333, width_m=100) for b, u in
                 [("promo-audio", "/categoria-prodotto/audio/"), ("promo-laptop", "/categoria-prodotto/laptop/"), ("promo-tablet", "/categoria-prodotto/tablet/")]],
               dir="row", dir_m="column", boxed=True, pad=(24, 20, 24, 20), gap=16)

    best = C(section_head("Classifica", "I più venduti", "Vedi tutti", "/negozio/?orderby=popularity"),
             SC('[best_selling_products limit="8" columns="4"]'), boxed=True, pad=(30, 20, 20, 20), gap=0)

    sale = C(IMG("banners/banner-sale-50", "/offerte-lampo/", 22),
             section_head(None, "Fino al -50% su una selezione di prodotti", "Tutte le offerte", "/offerte-lampo/"),
             SC('[sale_products limit="4" columns="4" orderby="price" order="ASC"]'), boxed=True, pad=(30, 20, 20, 20), gap=22)

    gamer = C(IMG("banners/banner-gamer-bundle", "/categoria-prodotto/gaming/", 22),
              SC('[products category="gaming" limit="4" columns="4" orderby="popularity"]'), boxed=True, pad=(30, 20, 20, 20), gap=22)

    brands = C(section_head("Marchi", "I marchi più amati", "Tutti i marchi", "/marchi/"), SC("[pishop_brands]"), boxed=True, pad=(30, 20, 30, 20), gap=0)

    reviews = [("Consegna in 24 ore e prodotto perfetto. Il servizio clienti mi ha aiutato a scegliere il laptop giusto per l’università.", "Giulia Rossi", "Studentessa, Bologna"),
               ("Prezzi onesti e offerte lampo davvero convenienti. Ho preso la PS5 con il pacchetto gamer e ho risparmiato parecchio.", "Marco Bianchi", "Cliente dal 2022, Torino"),
               ("Ho fatto un reso senza problemi e il rimborso è arrivato in tre giorni. Finalmente un e-commerce affidabile.", "Francesca Lombardi", "Napoli")]
    testi = C(section_head("Recensioni", "Cosa dicono i nostri clienti", center=True),
              C(*[C(W("testimonial", testimonial_content=f"⭐⭐⭐⭐⭐<br>{q}", testimonial_name=n, testimonial_job=j, testimonial_alignment="left", testimonial_image=m(f"brand/avatar-{k}"), image_size=size(52),
                      content_content_color=HEX["text"], name_text_color=HEX["black"], job_text_color=HEX["gray"],
                      content_typography_typography="custom", content_typography_font_size=size(15), content_typography_line_height=size(1.6, "em")),
                    width=33.333, width_m=100, bg="white", rad=18, pad=(26, 26, 26, 26), cls="pi-card") for k, (q, n, j) in enumerate(reviews)],
                dir="row", dir_m="column", gap=20),
              boxed=True, pad=(50, 20, 50, 20), bg="g100", gap=10)

    blog = C(section_head("Magazine", "Guide e novità dal blog", "Leggi il blog", "/blog/"), SC('[pishop_latest_posts n="3"]'),
             boxed=True, pad=(46, 20, 50, 20), gap=0)
    return [hero, cats, flash_wrap, new, promos, best, sale, gamer, brands, testi, blog]


# ══════════════════════════════════════════════════════════════════════
# INNER PAGES
# ══════════════════════════════════════════════════════════════════════
def offerte():
    _ctx.update(page="offerte", n=0)
    hero = C(C(SC('<span class="pi-eyebrow" style="background:#fff;color:#ff6a00">Solo per poco tempo</span>'),
               H("Offerte Lampo", "h1", 52, "white", sz_m=34), T("Sconti fino al 50% sui prodotti più desiderati. Scorte limitate.", "white", 17),
               SC("[pishop_countdown label=\"Termina tra\"]"), width=50, width_m=100, gap=12),
             boxed=True, bg_img="banners/flash-deals", pad=(70, 20, 70, 20), pad_m=(40, 16, 40, 16), minh=380, justify="center", cls="pi-dark",
             overlay=("rgba(17,17,17,0.85)", "rgba(17,17,17,0)"))
    flash = C(section_head("In scadenza", "Le offerte del momento"), SC('[pishop_flash_products columns="4" limit="8"]'), boxed=True, pad=(40, 20, 20, 20), gap=0)
    all_sale = C(section_head("Saldi", "Tutti i prodotti in sconto"), SC('[sale_products limit="16" columns="4"]'), boxed=True, pad=(30, 20, 20, 20), gap=0)
    ship = C(IMG("banners/banner-shipping", "/spedizioni-e-resi/", 20), boxed=True, pad=(20, 20, 50, 20))
    return [hero, flash, all_sale, ship]


def chi_siamo():
    _ctx.update(page="chi-siamo", n=0)
    hero = page_hero("Chi siamo", "Dal 2015 portiamo la tecnologia migliore nelle case degli italiani, con prezzi trasparenti e un servizio che mette le persone al centro.")
    story = C(
        C(SC('<span class="pi-eyebrow">La nostra storia</span>'), H("Nati a Milano, cresciuti con i nostri clienti", "h2", 34, sz_m=26),
          T("<p>PiShop nasce nel 2015 da un piccolo negozio di elettronica in Via Torino. La nostra idea era semplice: offrire online la stessa consulenza onesta che i clienti trovavano in negozio.</p><p>Oggi serviamo oltre <strong>120.000 clienti</strong> in tutta Italia, con un magazzino a Milano, spedizioni in 24/48 ore e un team di esperti che prova ogni prodotto prima di consigliarlo.</p>"),
          BTN("Scopri il negozio", "/negozio/"), width=50, width_m=100, gap=14, justify="center"),
        C(IMG("photos/team-scrivania", None, 22, cls="pi-img-round"), width=50, width_m=100),
        dir="row", dir_m="column", boxed=True, pad=(60, 20, 40, 20), gap=40, align="center")
    counters = C(*[C(W("counter", starting_number=0, ending_number=n, suffix=s, prefix="", thousand_separator="yes" if n > 9999 else "", thousand_separator_char=".",
                       title=t, number_color=HEX["orange"], title_color=HEX["black"], typography_number_typography="custom",
                       typography_number_font_family="Poppins", typography_number_font_size=size(46), typography_number_font_weight="800",
                       typography_title_typography="custom", typography_title_font_family="Inter", typography_title_font_size=size(15)),
                     width=25, width_m=50, bg="white", rad=18, pad=(26, 10, 26, 10), cls="pi-card")
                   for n, s, t in [(2015, "", "Anno di fondazione"), (120000, "+", "Clienti soddisfatti"), (48, "", "Ore max di consegna"), (4500, "+", "Prodotti in catalogo")]],
                 dir="row", wrap="m", boxed=True, pad=(40, 20, 40, 20), bg="g100", gap=20)
    values = C(section_head("I nostri valori", "Perché scegliere PiShop", center=True),
               C(*[C(ICONBOX(i, t, d, "top"), width=25, width_t=50, width_m=100, bg="white", rad=18, pad=(28, 20, 28, 20), border=((1, 1, 1, 1), "g200"))
                   for i, t, d in [("fas fa-check-circle", "Prodotti originali", "Solo prodotti nuovi e originali, con garanzia ufficiale Italia."),
                                   ("fas fa-tags", "Prezzi trasparenti", "Nessun costo nascosto: IVA e spedizione sempre indicate."),
                                   ("fas fa-user-friends", "Consulenza vera", "Il nostro team ti aiuta a scegliere, anche dopo l’acquisto."),
                                   ("fas fa-leaf", "Imballaggi sostenibili", "Cartone riciclato e spedizioni a impatto compensato.")]],
                 dir="row", wrap="m", gap=20), boxed=True, pad=(60, 20, 40, 20), gap=10)
    awards = C(section_head("Riconoscimenti", "Premi e certificazioni", center=True),
               C(*[C(ICONBOX("fas fa-award", t, d, "top", view="default"), width=20, width_t=33, width_m=50) for t, d in
                   [("E-commerce dell’anno", "Netcomm Awards 2025"), ("Miglior servizio clienti", "Categoria elettronica 2024"),
                    ("Negozio certificato", "Recensioni verificate 4,8/5"), ("Spedizioni green", "Partner logistico CO₂ neutral"),
                    ("Pagamenti sicuri", "Certificazione PCI DSS")]], dir="row", wrap="m", gap=10),
               boxed=True, pad=(30, 20, 40, 20), gap=10)
    team_members = [("Luca Ferri", "Fondatore e CEO"), ("Sara Conti", "Responsabile acquisti"), ("Davide Greco", "Customer care"), ("Elena Marino", "Marketing")]
    team = C(section_head("Il team", "Le persone dietro PiShop", center=True),
             C(C(IMG("photos/team-riunione", None, 22, cls="pi-img-round"), width=50, width_m=100),
               C(*[C(SC(f'<div style="width:64px;height:64px;border-radius:50%;background:#FFF1E6;color:#FF6A00;display:grid;place-items:center;font:800 22px Poppins">{"".join(w[0] for w in n.split())}</div>'),
                     H(n, "h4", 17, mb=0), T(r, "gray", 14), width=47, width_m=100, bg="white", rad=16, pad=(20, 20, 20, 20), gap=6,
                     border=((1, 1, 1, 1), "g200")) for n, r in team_members], width=50, width_m=100, dir="row", wrap=True, gap=16),
               dir="row", dir_m="column", gap=30, align="center"),
             boxed=True, pad=(40, 20, 60, 20), gap=10)
    cta = C(C(H("Hai domande? Siamo qui per te.", "h2", 30, "white", "center", sz_m=24), T("Scrivici o chiamaci: rispondiamo dal lunedì al sabato, 9:00–19:00.", "white", 16, "center"),
              BTN("Contattaci", "/contatti/", "dark", "center"), gap=10, align="center"),
            boxed=True, pad=(50, 20, 50, 20), bg="orange", rad=0)
    return [hero, story, counters, values, awards, team, cta]


def contatti():
    _ctx.update(page="contatti", n=0)
    hero = page_hero("Contatti", "Hai bisogno di aiuto con un ordine o vuoi un consiglio? Il nostro team ti risponde entro 24 ore lavorative.")
    cards = C(*[C(ICONBOX(i, t, d, "top"), width=33.333, width_m=100, bg="white", rad=18, pad=(30, 20, 30, 20), border=((1, 1, 1, 1), "g200"))
                for i, t, d in [("fas fa-phone-alt", "Telefono", "02 1234 5678<br>Lun–Sab 9:00–19:00"),
                                ("fas fa-envelope", "Email", "assistenza@pishop.example<br>Risposta entro 24 ore"),
                                ("fas fa-store", "Showroom", "Via Torino 21, 20123 Milano<br>Ritiro in negozio gratuito")]],
              dir="row", dir_m="column", boxed=True, pad=(50, 20, 30, 20), gap=20)
    form = C(
        C(H("Scrivici un messaggio", "h2", 28, sz_m=22), T("Compila il modulo: ti risponderemo il prima possibile.", "gray", 15),
          SC("[wpforms id=\"{{FORM_CONTACT}}\" title=\"false\"]"), width=55, width_m=100, gap=10, bg="white", rad=20, pad=(30, 30, 30, 30), cls="pi-card"),
        C(W("google_maps", address="Via Torino 21, Milano", zoom=size(15), height=size(420), _css_classes="pi-img-round"),
          width=45, width_m=100),
        dir="row", dir_m="column", boxed=True, pad=(20, 20, 60, 20), gap=30)
    return [hero, cards, form]


def faq():
    _ctx.update(page="faq", n=0)
    hero = page_hero("Domande frequenti", "Tutto quello che devi sapere su ordini, spedizioni, pagamenti, resi e garanzia.")
    groups = [
        ("Ordini", [("Come faccio a effettuare un ordine?", "Aggiungi i prodotti al carrello, clicca su <strong>Procedi al pagamento</strong> e completa i dati di spedizione. Puoi acquistare anche senza registrarti."),
                    ("Posso modificare o annullare un ordine?", "Sì, finché l’ordine non è stato spedito. Contattaci al più presto dalla pagina <a href=\"/contatti/\">Contatti</a> indicando il numero d’ordine."),
                    ("Come traccio il mio ordine?", "Usa la pagina <a href=\"/traccia-ordine/\">Traccia ordine</a> con numero d’ordine ed email, oppure accedi al tuo account.")]),
        ("Spedizioni", [("Quanto costa la spedizione?", "La spedizione standard in Italia costa 4,99 € ed è <strong>gratuita sopra i 49 €</strong>. Per l’Europa il costo è di 12,90 €."),
                        ("In quanto tempo arriva il mio ordine?", "In Italia consegniamo in 24/48 ore lavorative; isole e zone remote possono richiedere un giorno in più."),
                        ("Posso ritirare in negozio?", "Certo: scegli <em>Ritiro in negozio</em> al checkout e ritira gratuitamente nel nostro showroom di Milano.")]),
        ("Pagamenti", [("Quali metodi di pagamento accettate?", "Bonifico bancario e contrassegno. In negozio accettiamo anche carte e pagamenti contactless."),
                       ("Il pagamento è sicuro?", "Sì. Il sito usa connessione cifrata e non memorizziamo mai i dati della tua carta."),
                       ("Ricevo la fattura?", "Sì, puoi richiedere fattura indicando i dati fiscali al checkout. Riceverai anche la ricevuta via email.")]),
        ("Resi e garanzia", [("Come restituisco un prodotto?", "Hai <strong>14 giorni</strong> dalla consegna per esercitare il diritto di recesso. Il reso è gratuito: trovi tutti i dettagli in <a href=\"/spedizioni-e-resi/\">Spedizioni e resi</a>."),
                             ("Quando ricevo il rimborso?", "Entro 14 giorni dalla ricezione del reso, con lo stesso metodo di pagamento usato per l’ordine."),
                             ("Che garanzia hanno i prodotti?", "Tutti i prodotti hanno la garanzia legale di conformità di 24 mesi (Codice del Consumo).")]),
    ]
    blocks = []
    for title, qa in groups:
        children = [C(T(a, "text", 15), content_width="full", title=q) for q, a in qa]
        acc = {"id": uid(), "elType": "widget", "widgetType": "nested-accordion", "isInner": False, "elements": children,
               "settings": {"items": [{"_id": uid(), "item_title": q} for q, _ in qa], "title_tag": "h3", "default_state": "expanded",
                            "max_items_expended": "one", "accordion_item_title_space_between": size(10),
                            "accordion_background_normal_background": "classic", "accordion_background_normal_color": HEX["g100"],
                            "accordion_border_radius": radius(12), "accordion_padding": box(16, 20, 16, 20),
                            "title_typography_typography": "custom", "title_typography_font_family": "Poppins", "title_typography_font_size": size(16),
                            "title_typography_font_weight": "600", "normal_title_color": HEX["black"], "hover_title_color": HEX["orange"],
                            "active_title_color": HEX["orange"], "content_padding": box(10, 20, 14, 20)}}
        blocks.append(C(H(title, "h2", 24, mb=4), acc, gap=10, margin=(0, 0, 20, 0)))
    body = C(C(*blocks, width=68, width_m=100),
             C(C(H("Non trovi la risposta?", "h3", 22, "white"), T("Il nostro team ti risponde dal lunedì al sabato.", "g200", 15),
                 BTN("Contattaci", "/contatti/", "orange"), bg="black", rad=20, pad=(30, 26, 30, 26), gap=10), width=32, width_m=100),
             dir="row", dir_m="column", boxed=True, pad=(50, 20, 60, 20), gap=30)
    return [hero, body]


def blog_page():
    _ctx.update(page="blog", n=0)
    hero = page_hero("Il Magazine di PiShop", "Guide all’acquisto, recensioni e consigli dai nostri esperti di tecnologia.", "photos/laptop-chiuso", dark=True, crumbs="Blog")
    featured = C(section_head("In evidenza", "Ultimi articoli"), SC('[pishop_latest_posts n="3"]'), boxed=True, pad=(50, 20, 20, 20), gap=0)
    more = C(section_head("Archivio", "Altri articoli"), SC('[pishop_latest_posts n="6" offset="3"]'), boxed=True, pad=(30, 20, 60, 20), gap=0)
    return [hero, featured, more]


def marchi():
    _ctx.update(page="marchi", n=0)
    hero = page_hero("Marchi", "Rivenditori dei migliori brand della tecnologia, con prodotti originali e garanzia ufficiale Italia.")
    body = C(SC("[pishop_brands]"), boxed=True, pad=(50, 20, 30, 20))
    feat = C(section_head("In evidenza", "Prodotti in primo piano"), SC('[featured_products limit="8" columns="4"]'), boxed=True, pad=(20, 20, 60, 20), gap=0)
    return [hero, body, feat]


def simple_page(slug, title, subtitle, content, extra=None):
    _ctx.update(page=slug, n=0)
    hero = page_hero(title, subtitle)
    body = C(C(T(content, "text", 16, lh=1.75, cls="pi-legal"), width=75, width_t=100, width_m=100),
             C(C(H("Serve aiuto?", "h3", 20), T("Scrivici: rispondiamo entro 24 ore lavorative.", "gray", 14), BTN("Contattaci", "/contatti/", "orange", sz=14),
                 bg="g100", rad=18, pad=(24, 22, 24, 22), gap=8), width=25, width_t=100, width_m=100),
             dir="row", dir_t="column", boxed=True, pad=(50, 20, 60, 20), gap=40)
    out = [hero, body]
    if extra: out.insert(1, extra)
    return out


def tracking():
    _ctx.update(page="traccia", n=0)
    hero = page_hero("Traccia il tuo ordine", "Inserisci il numero d’ordine e l’email usata al checkout per vedere lo stato della spedizione.")
    body = C(C(SC("[woocommerce_order_tracking]"), width=60, width_m=100, bg="white", rad=20, pad=(30, 30, 30, 30), cls="pi-card"),
             boxed=True, pad=(50, 20, 60, 20), justify="center", align="center")
    return [hero, body]


def plugin_page(slug, title, subtitle, code):
    _ctx.update(page=slug, n=0)
    return [page_hero(title, subtitle), C(SC(code), boxed=True, pad=(40, 20, 60, 20))]


# ══════════════════════════════════════════════════════════════════════
def main():
    pages = [
        {"slug": "home", "title": "Home", "data": home(), "front": True},
        {"slug": "offerte-lampo", "title": "Offerte Lampo", "data": offerte()},
        {"slug": "chi-siamo", "title": "Chi siamo", "data": chi_siamo()},
        {"slug": "contatti", "title": "Contatti", "data": contatti()},
        {"slug": "faq", "title": "Domande frequenti", "data": faq()},
        {"slug": "blog", "title": "Blog", "data": blog_page()},
        {"slug": "marchi", "title": "Marchi", "data": marchi()},
        {"slug": "traccia-ordine", "title": "Traccia ordine", "data": tracking()},
        {"slug": "confronta", "title": "Confronta prodotti", "data": plugin_page("confronta", "Confronta prodotti", "Metti a confronto le caratteristiche dei prodotti che ti interessano.", "[woosc_list]"), "option": "woosc"},
        {"slug": "lista-desideri", "title": "Lista desideri", "data": plugin_page("lista-desideri", "Lista desideri", "I prodotti che hai salvato per dopo.", "[woosw_list]"), "option": "woosw"},
    ]
    for lp in LEGAL:
        pages.append({"slug": lp["slug"], "title": lp["title"], "data": simple_page(lp["slug"], lp["title"], lp["subtitle"], lp["content"]),
                      "option": lp.get("option")})
    templates = [{"slug": "pishop-header", "title": "PiShop – Header", "type": "type_header", "data": header()},
                 {"slug": "pishop-footer", "title": "PiShop – Footer", "type": "type_footer", "data": footer()}]
    os.makedirs(f"{ROOT}/data/build", exist_ok=True)
    json.dump({"templates": templates, "pages": pages}, open(f"{ROOT}/data/build/site.json", "w"), ensure_ascii=False)
    print(f"built {len(pages)} pages + {len(templates)} templates")


if __name__ == "__main__":
    main()
