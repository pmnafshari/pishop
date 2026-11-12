# PiShop: Project Description

## 1. Summary
**PiShop** is an Italian-language consumer-electronics online shop built with **WordPress + WooCommerce**. Every page is designed with the **Elementor page builder**. Its structure follows the reference template in `../OnlineShop/` (17 saved `.mhtml` pages of the iShop template), adapted for the Italian market and rebranded with an **orange / black / gray / white** palette.

| Item | Value |
|---|---|
| Shop name | PiShop |
| Language | Italian (`it_IT`) for the front end and the admin |
| Currency | Euro (€), Italian formatting (`1.299,00 €`) |
| Tax | IVA 22% (prices shown including VAT) |
| Local URL | http://onlineshop.local |
| Local dev env | Local (by Flywheel) 10.2: PHP 8.2, MySQL 8.4, nginx |
| CMS | WordPress 7.1.x |
| E-commerce | WooCommerce |
| Page builder | **Elementor** (all marketing pages + header/footer) |
| Theme | Astra (free) + `pishop-child` child theme |

## 2. Goals
1. Deliver a complete, working shop that runs end to end: browse → product → cart → checkout → order → account.
2. Rebuild the reference structure, all text in Italian, and add every page an Italian e-commerce site legally needs.
3. Build the pages with a page builder (Elementor) so a non-developer can edit them visually.
4. Keep everything reproducible from scripts in this repo (WP-CLI), so the site can be rebuilt from scratch.
5. Keep a portfolio-grade repo: clear docs, no secrets committed, clean structure.

## 3. Brand & design system
| Token | Hex | Use |
|---|---|---|
| `--pi-orange` | `#FF6A00` | Primary: buttons, prices, badges, links, highlights |
| `--pi-orange-dark` | `#E05A00` | Hover/active states |
| `--pi-orange-light` | `#FFF1E6` | Soft backgrounds, chips |
| `--pi-black` | `#111111` | Header bar, headings, footer background |
| `--pi-gray-900` | `#2B2B2B` | Body text |
| `--pi-gray-500` | `#6B7280` | Secondary text, meta |
| `--pi-gray-200` | `#E5E7EB` | Borders, dividers |
| `--pi-gray-100` | `#F4F5F7` | Section backgrounds, cards |
| `--pi-white` | `#FFFFFF` | Main background, text on dark |

- Typography: **Poppins** (headings) + **Inter** (body), from Google Fonts.
- Radius 12px on cards, 999px on pills/buttons, soft shadows.
- Logo: a text/SVG wordmark "**Pi**Shop" with an orange "π" mark.

## 4. Information architecture (sitemap)

### 4.1 Pages taken from the reference (Persian → Italian)
| # | Reference page | Italian page | Slug | Built with |
|---|---|---|---|---|
| 1 | صفحه اصلی | Home | `/` | Elementor |
| 2 | فروشگاه | Negozio | `/negozio/` | WooCommerce archive + Elementor header/footer |
| 3 | (6 product pages) | Scheda prodotto | `/prodotto/<slug>/` | WooCommerce single + tabs |
| 4 | سبد خرید | Carrello | `/carrello/` | WooCommerce block |
| 5 | حساب کاربری من | Il mio account | `/mio-account/` | WooCommerce |
| 6 | مقایسه محصول | Confronta prodotti | `/confronta/` | WPC Smart Compare |
| 7 | شگفت انگیز شو | Offerte Lampo | `/offerte-lampo/` | Elementor + countdown |
| 8 | وبلاگ | Blog / Magazine | `/blog/` | Elementor + posts |
| 9 | (blog article) | Articolo | `/<post-slug>/` | WP post |
| 10 | درباره ما | Chi siamo | `/chi-siamo/` | Elementor |
| 11 | تماس با ما | Contatti | `/contatti/` | Elementor + form |
| 12 | سوالات متداول | Domande frequenti | `/faq/` | Elementor accordion |

### 4.2 Pages added (missing from the reference, needed for a real IT shop)
| Page | Slug | Why |
|---|---|---|
| Cassa (Checkout) | `/cassa/` | Needed to complete an order |
| Lista desideri (Wishlist) | `/lista-desideri/` | Reference has heart icons |
| Marchi (Brands) | `/marchi/` | Reference has a brands section |
| Spedizioni e resi | `/spedizioni-e-resi/` | Consumer info, EU 14-day withdrawal right |
| Termini e condizioni | `/termini-e-condizioni/` | Required (Codice del Consumo) |
| Privacy Policy | `/privacy-policy/` | Required (GDPR) |
| Cookie Policy | `/cookie-policy/` | Required (Garante Privacy) |
| Traccia ordine | `/traccia-ordine/` | Customer service |
| 404 | (theme) | Error page, as in the reference menu |

### 4.3 Home page sections (reference order, Italian copy)
1. Top promo bar ("Spedizione gratuita sopra 49 €")
2. Header: logo, search, account, wishlist, cart · mega-menu "Categorie"
3. Hero slider (3 slides) + 2 side banners
4. "Offerte Lampo" with countdown + product carousel
5. Popular categories (icon tiles)
6. "Nuovi arrivi" product grid
7. Triple promo banners
8. "I più venduti" product grid
9. "Fino al -50%" sale grid
10. "Pacchetto Gamer" bundle banner
11. Popular brands
12. Benefits strip (spedizione, reso 14 giorni, pagamenti sicuri, assistenza)
13. Blog: latest articles
14. Newsletter
15. Footer: quick links, customer guide, categories, contact, social, payments, P.IVA

## 5. Catalog
**Categories** (from the reference mega-menu): Smartphone · Laptop · Cuffie e Audio · Gaming · Smartwatch · Speaker · Power bank · Tablet · Computer e Monitor · Accessori.

- About 30 demo products spread across these categories, with Italian names, descriptions, specs (attributes), regular and sale prices, stock, ratings and brands.
- Product types shown: simple, variable (color/storage), on-sale, out of stock, "external/affiliate". The reference shows all of these.
- Brand taxonomy (WooCommerce Brands): Apple, Samsung, Xiaomi, Sony, Lenovo, JBL, Anker, Microsoft…

## 6. Plugins (all free, from wordpress.org)
| Plugin | Purpose |
|---|---|
| WooCommerce | Shop engine (cart, checkout, orders, accounts, brands) |
| Elementor | **Page builder** |
| Ultimate Addons for Elementor (Header Footer Elementor) | Header and footer built in Elementor |
| WPC Smart Compare for WooCommerce | Product comparison page |
| WPC Smart Wishlist for WooCommerce | Wishlist |
| WPForms Lite | Contact form + newsletter form (Contact Form 7 needs PHP 8.3; the site runs 8.2) |
| *(before going public)* Complianz or similar | Cookie banner (IT law) |

## 7. Imagery
- Banners, hero slides and category tiles are **generated locally** with a Python script (`scripts/make_images.py`) in the brand palette. No copyrighted assets from the reference.
- Product photos come from free-license sources; their sources are listed in `assets/CREDITS.md`.
- Images are optimized (WebP/JPG, ≤ 1600px wide) before upload.

## 8. Repository layout
```
PiShop/
├── project.md          ← this file
├── steps.md            ← progress log (done / todo)
├── rules.md            ← guardrails & red lines
├── .gitignore
├── bin/wp              ← WP-CLI wrapper bound to the Local site
├── scripts/            ← reproducible setup scripts (WP-CLI / PHP / Python)
├── data/               ← products.json, pages content, menus
├── assets/images/      ← generated / sourced images (+ CREDITS.md)
└── theme/pishop-child/ ← child theme (palette CSS, small PHP tweaks)
```

## 9. Definition of done
- [ ] Every page in §4 exists, is in Italian, and is reachable from the menu or footer.
- [ ] The Home page and the marketing pages are built and editable in Elementor.
- [ ] You can buy a product end to end with "Bonifico bancario" / "Contrassegno" (test payment methods).
- [ ] Cart, checkout, account, compare and wishlist all work.
- [ ] Palette applied consistently; responsive on mobile (375px), tablet and desktop.
- [ ] No PHP errors in `debug.log`; no broken images or links.
- [ ] No secrets in the repo; `.gitignore` in place.
