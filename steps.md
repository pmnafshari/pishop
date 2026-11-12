# PiShop: Steps Log

Legend: ✅ done · 🔄 in progress · ⬜ to do · ⚠️ blocked/issue

## Phase 0: Environment
- ✅ 0.1 Install Local (by Flywheel) in `/Applications/Local.app` (Homebrew cask `local` 10.2.0)
- ✅ 0.2 Create the Local site "OnlineShop" → http://onlineshop.local (PHP 8.2.29, MySQL 8.4, nginx 1.26)
- ✅ 0.3 Create the WP-CLI wrapper `bin/wp` (Local's PHP + MySQL socket + bundled wp-cli.phar; sub-processes inherit the ini via PHPRC/PHP_INI_SCAN_DIR)
- ✅ 0.4 Analyze the reference template (`../OnlineShop/*.mhtml`, 17 pages): sitemap, home sections, mega-menu
- ✅ 0.5 Write `project.md`, `rules.md`, `steps.md`, `.gitignore`
- ✅ 0.6 `git init` + first commit
- ⚠️ 0.7 macOS 27 + Local PHP-FPM crash on outbound HTTPS (`objc … fork()` SIGABRT → 502 on wp-login). Fixed with `WP_HTTP_BLOCK_EXTERNAL` for web requests only (in the local wp-config, not in the repo). WP-CLI unaffected.

## Phase 1: Core setup ✅
- ✅ 1.1 DB backups in `../backups/` (outside the repo) before every destructive step
- ✅ 1.2 Italian (`it_IT`), Europe/Rome, `d/m/Y`
- ✅ 1.3 Title "PiShop", tagline, `/%postname%/`
- ✅ 1.4 Astra + `pishop-child` (symlinked from `theme/`)
- ✅ 1.5 Plugins: WooCommerce 11.3, Elementor 4.4, Header Footer Elementor 2.9, WPC Compare 6.7, WPC Wishlist 6.2, WPForms Lite 2.0 (CF7 needs PHP 8.3, so WPForms instead)
- ✅ 1.6 Italian language packs
- ✅ 1.7 Default content removed

## Phase 2: WooCommerce ✅
- ✅ 2.1 Store in Milano, EUR, `1.299,00 €` format, Italian slugs (negozio, carrello, cassa, mio-account, prodotto, categoria-prodotto)
- ✅ 2.2 IVA 22%, prices include VAT
- ✅ 2.3 Zones: Italia (4,99 €, free ≥ 49 €, store pickup) and Europa (12,90 €); paid rate hidden when free shipping applies
- ✅ 2.4 Bonifico + Contrassegno (test)
- ✅ 2.5 Woo pages renamed/Italianised

## Phase 3: Brand & assets ✅
- ✅ 3.1 Elementor kit: Global Colors (orange/black/gray/white) + Fonts (Poppins/Inter)
- ✅ 3.2 Logo "π PiShop" (SVG + PNG), favicon
- ✅ 3.3 Hero slides, 6 promo banners, flash-deal/about/shipping banners (`make_banners.py`)
- ✅ 3.4 Original product renders (`render_products.py`) + 11 CC photos, credited in `assets/CREDITS.md`
- ✅ 3.5 Child-theme CSS: cards, -% badges, Novità badge, stock bar, countdown, sidebar, forms, mobile header

## Phase 4: Catalog ✅
- ✅ 4.1 10 categories with images
- ✅ 4.2 14 brands (WooCommerce Brands)
- ✅ 4.3 Global attribute Colore + spec attributes (Scheda tecnica)
- ✅ 4.4 34 products: 3 variable, 1 external, 2 out of stock, 9 flash-sale with end date
- ✅ 4.5 Reviews (2–4 per product), sales counters for "Più venduti"

## Phase 5: Pages (Elementor) ✅
- ✅ 5.1 Header: top bar, logo, search, account/compare/wishlist/cart icons, menu with category dropdown
- ✅ 5.2 Footer: benefits, newsletter, 5 columns, legal bar, payment chips
- ✅ 5.3 Home: hero slideshow + side banners, categories, flash deals + countdown, new arrivals, promo banners, best sellers, sale banner + grid, gamer bundle, brands, reviews, blog
- ✅ 5.4 Offerte Lampo · 5.5 Chi siamo · 5.6 Contatti (WPForms + map) · 5.7 FAQ (nested accordion)
- ✅ 5.8 Blog page + 6 articles with photos
- ✅ 5.9 Marchi · 5.10 Confronta, Lista desideri
- ✅ 5.11 Spedizioni e resi, Termini (Woo terms page), Privacy (WP privacy page), Cookie, Traccia ordine
- ✅ 5.12 Menu principale + shop sidebar filters (categories, price, colour, rating)

## Phase 6: QA
- ✅ 6.1 End-to-end purchase in the browser: product → cart → checkout → order #335 (Contrassegno, free shipping, stock decremented)
- ✅ 6.2 Responsive: no horizontal scroll at 375px on 15 pages; mobile header/menu fixed
- ✅ 6.3 All pages HTTP 200 (404 page → 404); debug.log has no errors from PiShop code
- ✅ 6.4 README + one-command `scripts/setup.sh`
- ✅ 6.5 Mega menu redesign (iShop pattern): "Categorie" trigger → full-width panel with emoji category list + hover pane (Marchi / Fascia di prezzo / Scopri + best-seller card); links go to real filtered results (`?product_brand=`, `?min_price=&max_price=`, `?orderby=`); mobile slide-in drawer with drill-down; Esc/aria-expanded/hover-intent; cached in a transient, refreshed on product/category changes
- ⬜ 6.6 Before any public deploy: cookie banner, real legal texts, remove `WP_HTTP_BLOCK_EXTERNAL`, `DISALLOW_FILE_EDIT`, HTTPS (see rules.md §10)

---
## Notes / decisions
- Elementor **free** has no WooCommerce widgets, so product grids use WooCommerce shortcodes inside Elementor *Shortcode* widgets.
- The header/footer use *Header Footer Elementor*, because Theme Builder needs Elementor Pro. The hero slider is a container **background slideshow** (free) with live, editable text.
- Astra "modern" cards hardcode the sale label, so the shop uses Astra's grid style plus the child-theme `-%` badge.
- Product images are original illustrations (consistent look, no licensing risk); real CC photos are used for lifestyle, blog and about-page imagery.
