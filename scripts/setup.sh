#!/bin/bash
# PiShop – rebuild the whole site from this repo (idempotent).
# Usage: scripts/setup.sh            (full run)
#        SKIP_IMAGES=1 scripts/setup.sh   (reuse already generated images)
set -euo pipefail
cd "$(dirname "$0")/.."
WP=bin/wp
mkdir -p ../backups
echo "▸ Backup DB → ../backups/"
$WP db export "../backups/pishop-$(date +%Y%m%d-%H%M%S).sql" --quiet

echo "▸ Plugins & theme"
$WP theme is-installed astra || $WP theme install astra
for p in woocommerce elementor header-footer-elementor woo-smart-compare woo-smart-wishlist wpforms-lite; do
  $WP plugin is-installed $p || $WP plugin install $p
  $WP plugin activate $p >/dev/null
done
$WP language plugin install --all it_IT >/dev/null 2>&1 || true

scripts/01-core.sh

if [ -z "${SKIP_IMAGES:-}" ]; then
  echo "▸ Generating images (product renders, banners)"
  python3 -I scripts/render_products.py "$PWD"
  python3 -I scripts/make_banners.py "$PWD"
fi

echo "▸ Catalog";  $WP eval-file scripts/import-catalog.php
echo "▸ Media";    $WP eval-file scripts/import-media.php
echo "▸ Pages";    python3 -I scripts/build_pages.py "$PWD"; $WP eval-file scripts/apply-pages.php
$WP elementor flush-css >/dev/null
echo "✔ PiShop ready → http://onlineshop.local"
