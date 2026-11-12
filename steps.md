# PiShop: Steps Log

Legend: ✅ done · 🔄 in progress · ⬜ to do · ⚠️ blocked/issue

## Phase 0: Environment
- ✅ 0.1 Install Local (by Flywheel) in `/Applications/Local.app` (Homebrew cask `local` 10.2.0)
- ✅ 0.2 Create the Local site "OnlineShop" → http://onlineshop.local (PHP 8.2.29, MySQL 8.4, nginx 1.26)
- ✅ 0.3 Create the WP-CLI wrapper `bin/wp` (uses Local's PHP, MySQL socket and the bundled wp-cli.phar)
- ✅ 0.4 Analyze the reference template (`../OnlineShop/*.mhtml`, 17 pages): sitemap, home sections, mega-menu
- ✅ 0.5 Write `project.md`, `rules.md`, `steps.md`, `.gitignore`
- ⬜ 0.6 `git init` + first commit (docs only)

## Phase 1: Core setup
- ⬜ 1.1 Back up the fresh DB (outside the repo)
- ⬜ 1.2 Set the language to Italian (`it_IT`), timezone Europe/Rome, date format `d/m/Y`
- ⬜ 1.3 Site title "PiShop", tagline, pretty permalinks `/%postname%/`
- ⬜ 1.4 Install the Astra theme + create and activate the `pishop-child` child theme
- ⬜ 1.5 Install plugins: WooCommerce, Elementor, Header Footer Elementor, WPC Compare, WPC Wishlist, Contact Form 7
- ⬜ 1.6 Install Italian language packs for all plugins
- ⬜ 1.7 Remove default content (Hello World, Sample Page, Twenty* themes)

## Phase 2: WooCommerce configuration
- ⬜ 2.1 Store address (Milano, IT), currency EUR, Italian number format
- ⬜ 2.2 IVA 22% tax, prices entered including VAT
- ⬜ 2.3 Shipping zones: Italia (standard 4,99 €, free above 49 €), EU
- ⬜ 2.4 Payments: Bonifico, Contrassegno (test only)
- ⬜ 2.5 Woo pages: Negozio, Carrello, Cassa, Il mio account (Italian slugs)

## Phase 3: Brand & assets
- ⬜ 3.1 Elementor global colors and fonts (palette from project.md §3)
- ⬜ 3.2 Logo (SVG) + favicon
- ⬜ 3.3 Generate banners, hero slides and category tiles (`scripts/make_images.py`)
- ⬜ 3.4 Product images + `assets/CREDITS.md`
- ⬜ 3.5 Child-theme CSS (buttons, product cards, badges, Woo pages)

## Phase 4: Catalog
- ⬜ 4.1 Product categories (10) with images
- ⬜ 4.2 Brands
- ⬜ 4.3 Attributes (Colore, Memoria, …)
- ⬜ 4.4 Import about 30 products from `data/products.json` (simple, variable, sale, out-of-stock, external)
- ⬜ 4.5 Demo reviews / ratings

## Phase 5: Pages (Elementor)
- ⬜ 5.1 Header (top bar, logo, search, icons, menu) with Header Footer Elementor
- ⬜ 5.2 Footer
- ⬜ 5.3 Home (all 15 sections)
- ⬜ 5.4 Offerte Lampo
- ⬜ 5.5 Chi siamo
- ⬜ 5.6 Contatti (+ CF7 form)
- ⬜ 5.7 FAQ
- ⬜ 5.8 Blog page + 4 articles
- ⬜ 5.9 Marchi
- ⬜ 5.10 Confronta, Lista desideri
- ⬜ 5.11 Legal: Termini, Privacy, Cookie, Spedizioni e resi, Traccia ordine
- ⬜ 5.12 Menus (primary, mega-menu categories, footer)

## Phase 6: QA
- ⬜ 6.1 End-to-end purchase test (guest + registered)
- ⬜ 6.2 Responsive check (375 / 768 / 1280)
- ⬜ 6.3 Broken links/images, debug.log clean
- ⬜ 6.4 Final commit + README with screenshots

---
## Notes / decisions
- Elementor **free** has no WooCommerce widgets, so product grids use WooCommerce shortcodes/blocks inside Elementor *Shortcode* widgets.
- The header and footer come from *Header Footer Elementor*, because Theme Builder needs Elementor Pro.
