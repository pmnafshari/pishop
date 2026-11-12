# PiShop: Rules, Guardrails & Red Lines

These rules apply to every change made to this project, whether a person or an AI assistant makes it.
🔴 = **red line** (never break it) · 🟠 = guardrail (break it only for a written reason, recorded in `steps.md`).

---

## 1. Secrets & credentials
- 🔴 **Never commit secrets.** That covers `wp-config.php`, `.env`, DB dumps, API keys, SMTP passwords, payment keys (Stripe/PayPal), license keys, salts, and `auth.json`.
- 🔴 Never paste real credentials into `steps.md`, `project.md`, commits, issues, or screenshots.
- 🔴 Payment gateways stay in **test/sandbox mode** only. Never put live keys in a local or demo site.
- 🟠 Local default DB credentials (`root/root`) exist only inside Local's own config and must not be copied into repo files.
- 🟠 Before every commit, run: `git status` and `git diff --cached | grep -iE "password|secret|api[_-]?key|token|BEGIN (RSA|OPENSSH)"`. It must return nothing.
- 🔴 `.gitignore` must exist **before** the first commit (see §8).

## 2. Data & privacy (GDPR)
- 🔴 No real customer data. Demo orders and users only use fictitious names and `@example.com` emails.
- 🔴 Never export or commit the database, `wp-content/uploads/wc-logs`, or the `woocommerce_uploads` folder.
- 🟠 The site must have a Privacy Policy, a Cookie Policy, and a cookie-consent banner before it is shown publicly.

## 3. WordPress core & files
- 🔴 **Never edit WordPress core** (`wp-admin/`, `wp-includes/`, root `wp-*.php`) or plugin source code. Updates would wipe the changes, and editing them is unsafe.
- 🔴 Never edit the parent theme (Astra). All custom code goes in the **`pishop-child`** child theme or in a script in `scripts/`.
- 🟠 Use hooks/filters and Elementor settings, not template overrides, unless an override is unavoidable. If it is, keep it in the child theme and note why.
- 🟠 Keep PHP snippets small and namespaced (`pishop_` prefix) to avoid collisions.

## 4. Plugins & dependencies
- 🔴 Install plugins/themes **only from wordpress.org or the official vendor**. No "nulled" or cracked premium plugins.
- 🟠 Use free plugins only (Elementor free, not Pro). Each plugin must earn its place; no duplicates (for example, two wishlist plugins).
- 🟠 Pin versions in `steps.md` when installing; update one plugin at a time, then retest.

## 5. Content & assets (copyright)
- 🔴 **Do not reuse images, logos, or text from the reference template** (`../OnlineShop/*.mhtml`). It is structure inspiration only.
- 🔴 Every third-party image must have a free license (CC0 / CC-BY / Unsplash/Pexels license). Record its source in `assets/CREDITS.md`.
- 🟠 Brand names (Apple, Samsung…) appear only as product attributes in a demo context. Do not imitate their official stores or logos as PiShop branding.
- 🟠 All visible text is **Italian**, with correct accents (è, à, ù, perché). No leftover Persian/English placeholder text or "Lorem ipsum" on finished pages.

## 6. Design system
- 🟠 Use only the palette tokens from `project.md §3`: orange `#FF6A00`, black `#111111`, grays, white. No random new colors.
- 🟠 Text contrast ≥ WCAG AA (4.5:1 for body text). White text on orange is only for large/bold text and buttons.
- 🟠 Every page must be checked at 375px, 768px and 1280px widths before it is marked done.
- 🟠 Images: max 1600px wide, compressed, with an Italian `alt` text on every image.

## 7. Page builder discipline
- 🔴 **Build pages with Elementor.** Do not hardcode page layouts in PHP templates.
- 🟠 Use Elementor **Global Colors / Global Fonts** (set to the palette), not per-widget hex values.
- 🟠 Use sections/containers, not inline HTML widgets, unless no widget fits (for example, a WooCommerce shortcode).
- 🟠 After bulk edits, run *Elementor → Tools → Regenerate CSS* (`wp elementor flush-css`).

## 8. Git & repository
- 🔴 Never commit: `wp-config.php`, `.env*`, `*.sql`, `*.sql.gz`, `*.log`, `uploads/`, `node_modules/`, `vendor/`, `.DS_Store`, backups (`*.bak`, `*.zip`, `*.wpress`).
- 🟠 Small commits with clear messages (`feat:`, `fix:`, `docs:`, `chore:`).
- 🟠 Never force-push `main`. Never rewrite published history.
- 🟠 `steps.md` is updated in the same commit as the work it describes.

## 9. Safe operations
- 🔴 **Back up before destructive actions.** Run `bin/wp db export` into a backup folder **outside the repo** before search-replace, bulk deletes, or plugin removal.
- 🔴 Never run `wp db reset`, `wp site empty`, or `DROP` commands without a fresh backup and explicit approval.
- 🟠 Use `wp search-replace --dry-run` first, always.
- 🟠 Scripts must be **idempotent**: running them twice must not create duplicate pages, products or menus. Check by slug/SKU first.

## 10. Security baseline (before anything goes online)
- 🔴 No `admin` username; strong admin password; `WP_DEBUG_DISPLAY` false in production.
- 🟠 `DISALLOW_FILE_EDIT` true in production; HTTPS only; keep core/plugins updated.
- 🟠 Remove demo users and the `local-xdebuginfo.php` file on any public deploy.

## 11. Quality gates (a step is "done" only if all of these pass)
1. The page loads with HTTP 200, with no PHP notices in `wp-content/debug.log`.
2. No broken images/links (checked in the browser).
3. Italian copy proofread; palette respected.
4. Responsive check passed (§6).
5. `steps.md` updated.
