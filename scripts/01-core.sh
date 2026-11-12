#!/bin/bash
# PiShop – Phase 1 & 2: core + WooCommerce configuration (idempotent)
set -euo pipefail
cd "$(dirname "$0")/.."
WP=bin/wp
THEMES_DIR="$HOME/Local Sites/onlineshop/app/public/wp-content/themes"

echo "▸ Language, time, permalinks"
$WP language core is-installed it_IT || $WP language core install it_IT
$WP site switch-language it_IT >/dev/null
$WP option update timezone_string Europe/Rome >/dev/null
$WP option update date_format 'd/m/Y' >/dev/null
$WP option update time_format 'H:i' >/dev/null
$WP option update blogname 'PiShop' >/dev/null
$WP option update blogdescription 'Elettronica, smartphone e gaming al miglior prezzo' >/dev/null
$WP rewrite structure '/%postname%/' >/dev/null

echo "▸ Child theme (symlinked from repo)"
[ -e "$THEMES_DIR/pishop-child" ] || ln -s "$PWD/theme/pishop-child" "$THEMES_DIR/pishop-child"
$WP theme activate pishop-child >/dev/null
for t in twentytwentythree twentytwentyfour; do $WP theme is-installed $t && $WP theme delete $t >/dev/null || true; done

echo "▸ Remove default content"
for slug in hello-world sample-page refund_returns; do
  id=$($WP post list --post_type=post,page --name="$slug" --post_status=any --field=ID)
  [ -n "$id" ] && $WP post delete $id --force >/dev/null || true
done
$WP comment delete $($WP comment list --field=ID) --force >/dev/null 2>&1 || true

echo "▸ WooCommerce pages → Italian titles/slugs"
rename_page() { $WP post update "$($WP option get "$1")" --post_title="$2" --post_name="$3" >/dev/null; }
rename_page woocommerce_shop_page_id      'Negozio'        negozio
rename_page woocommerce_cart_page_id      'Carrello'       carrello
rename_page woocommerce_checkout_page_id  'Cassa'          cassa
rename_page woocommerce_myaccount_page_id 'Il mio account' mio-account

echo "▸ Store settings (Italy, EUR, IVA)"
o() { $WP option update "$1" "$2" >/dev/null 2>&1 || true; }
o woocommerce_store_address 'Via Torino 21'
o woocommerce_store_city 'Milano'
o woocommerce_store_postcode '20123'
o woocommerce_default_country 'IT:MI'
o woocommerce_allowed_countries 'specific'
$WP option update woocommerce_specific_allowed_countries '["IT","SM","VA","FR","DE","ES","AT","CH"]' --format=json >/dev/null
o woocommerce_ship_to_countries ''
o woocommerce_currency 'EUR'
o woocommerce_currency_pos 'right_space'
o woocommerce_price_thousand_sep '.'
o woocommerce_price_decimal_sep ','
o woocommerce_price_num_decimals '2'
o woocommerce_weight_unit 'kg'
o woocommerce_dimension_unit 'cm'
o woocommerce_calc_taxes 'yes'
o woocommerce_prices_include_tax 'yes'
o woocommerce_tax_display_shop 'incl'
o woocommerce_tax_display_cart 'incl'
o woocommerce_price_display_suffix 'IVA inclusa'
o woocommerce_tax_based_on 'base'
o woocommerce_enable_reviews 'yes'
o woocommerce_review_rating_verification_required 'no'
o woocommerce_enable_guest_checkout 'yes'
o woocommerce_enable_signup_and_login_from_checkout 'yes'
o woocommerce_enable_myaccount_registration 'yes'
o woocommerce_manage_stock 'yes'
o woocommerce_coming_soon 'no'
o woocommerce_store_pages_only 'no'
o woocommerce_onboarding_profile '{"skipped":true}'
o woocommerce_task_list_hidden 'yes'
o woocommerce_show_marketplace_suggestions 'no'
o woocommerce_allow_tracking 'no'
$WP option update woocommerce_permalinks '{"product_base":"prodotto","category_base":"categoria-prodotto","tag_base":"tag-prodotto","attribute_base":"","use_verbose_page_rules":false}' --format=json >/dev/null

echo "▸ Tax rate IVA 22%"
if [ "$($WP db query "SELECT COUNT(*) FROM wp_woocommerce_tax_rates WHERE tax_rate_country='IT'" --skip-column-names)" = "0" ]; then
  $WP eval 'WC_Tax::_insert_tax_rate(["tax_rate_country"=>"IT","tax_rate"=>"22.0000","tax_rate_name"=>"IVA","tax_rate_priority"=>1,"tax_rate_shipping"=>1,"tax_rate_order"=>0,"tax_rate_class"=>""]);'
fi

echo "▸ Shipping zones"
$WP eval '
if ( ! count( WC_Shipping_Zones::get_zones() ) ) {
  $z = new WC_Shipping_Zone(); $z->set_zone_name("Italia"); $z->set_zone_order(1);
  $z->add_location("IT","country"); $z->save();
  $id = $z->add_shipping_method("flat_rate");
  update_option("woocommerce_flat_rate_{$id}_settings", ["title"=>"Spedizione standard (24/48h)","tax_status"=>"taxable","cost"=>"4.99"]);
  $id = $z->add_shipping_method("free_shipping");
  update_option("woocommerce_free_shipping_{$id}_settings", ["title"=>"Spedizione gratuita","requires"=>"min_amount","min_amount"=>"49","ignore_discounts"=>"no"]);
  $id = $z->add_shipping_method("local_pickup");
  update_option("woocommerce_local_pickup_{$id}_settings", ["title"=>"Ritiro in negozio (Milano)","tax_status"=>"none","cost"=>"0"]);
  $e = new WC_Shipping_Zone(); $e->set_zone_name("Europa"); $e->set_zone_order(2);
  foreach (["SM","VA","FR","DE","ES","AT","CH"] as $c) $e->add_location($c,"country"); $e->save();
  $id = $e->add_shipping_method("flat_rate");
  update_option("woocommerce_flat_rate_{$id}_settings", ["title"=>"Spedizione Europa (3-5 giorni)","tax_status"=>"taxable","cost"=>"12.90"]);
  echo "zones created\n";
}'

echo "▸ Payment methods (test only)"
$WP option update woocommerce_bacs_settings '{"enabled":"yes","title":"Bonifico bancario","description":"Effettua il pagamento tramite bonifico. Usa il numero d’ordine come causale.","instructions":"Il tuo ordine verrà spedito dopo la ricezione del bonifico."}' --format=json >/dev/null
$WP option update woocommerce_cod_settings '{"enabled":"yes","title":"Contrassegno","description":"Paga in contanti alla consegna.","instructions":"Paga in contanti al corriere alla consegna.","enable_for_methods":[],"enable_for_virtual":"no"}' --format=json >/dev/null
$WP option update woocommerce_cheque_settings '{"enabled":"no"}' --format=json >/dev/null

$WP rewrite flush >/dev/null
echo "✔ core done"
