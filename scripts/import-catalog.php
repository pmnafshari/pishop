<?php
/**
 * PiShop – catalog importer (idempotent: matches categories by slug, products by SKU).
 *
 * Run: bin/wp eval-file scripts/import-catalog.php
 */

defined( 'ABSPATH' ) || exit;
require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

$root    = dirname( __DIR__ );
$catalog = json_decode( file_get_contents( "$root/data/catalog.json" ), true );

/**
 * Import a local image into the media library once (keyed by file name).
 */
function pishop_media( $path, $alt = '' ) {
	$key   = 'pishop_src_' . md5( basename( $path ) );
	$found = get_posts( array( 'post_type' => 'attachment', 'meta_key' => '_pishop_src', 'meta_value' => $key, 'fields' => 'ids', 'numberposts' => 1 ) );
	if ( $found ) {
		return (int) $found[0];
	}
	$tmp = wp_tempnam( basename( $path ) );
	copy( $path, $tmp );
	$id = media_handle_sideload( array( 'name' => basename( $path ), 'tmp_name' => $tmp ), 0, $alt );
	if ( is_wp_error( $id ) ) {
		WP_CLI::warning( $id->get_error_message() . " ($path)" );
		return 0;
	}
	update_post_meta( $id, '_pishop_src', $key );
	update_post_meta( $id, '_wp_attachment_image_alt', $alt );
	return (int) $id;
}

function pishop_term( $name, $tax, $slug = '', $desc = '' ) {
	$slug = $slug ? $slug : sanitize_title( $name );
	$t    = get_term_by( 'slug', $slug, $tax );
	if ( $t ) {
		return (int) $t->term_id;
	}
	$r = wp_insert_term( $name, $tax, array( 'slug' => $slug, 'description' => $desc ) );
	return is_wp_error( $r ) ? 0 : (int) $r['term_id'];
}

/* ── Categories ─────────────────────────────────────────────────────── */
$cat_ids = array();
foreach ( $catalog['categories'] as $i => $c ) {
	$id = pishop_term( $c['name'], 'product_cat', $c['slug'], $c['desc'] );
	$img = pishop_media( "$root/assets/images/categories/{$c['slug']}.png", $c['name'] );
	update_term_meta( $id, 'thumbnail_id', $img );
	update_term_meta( $id, 'order', $i );
	update_term_meta( $id, 'pishop_emoji', $c['emoji'] ?? '' );
	$cat_ids[ $c['slug'] ] = $id;
}
// Default "Uncategorized" → Italian, keep hidden from menus.
$unc = get_option( 'default_product_cat' );
if ( $unc ) {
	wp_update_term( (int) $unc, 'product_cat', array( 'name' => 'Senza categoria', 'slug' => 'senza-categoria' ) );
}
WP_CLI::log( 'Categories: ' . count( $cat_ids ) );

/* ── Brands ─────────────────────────────────────────────────────────── */
$brand_ids = array();
foreach ( $catalog['brands'] as $b ) {
	$brand_ids[ $b ] = pishop_term( $b, 'product_brand' );
}

/* ── Tags ───────────────────────────────────────────────────────────── */
$tag_map = array(
	'nuovo'      => pishop_term( 'Novità', 'product_tag', 'novita' ),
	'bestseller' => pishop_term( 'Più venduti', 'product_tag', 'piu-venduti' ),
	'lampo'      => pishop_term( 'Offerta lampo', 'product_tag', 'offerta-lampo' ),
);

/* ── Global attribute: Colore ──────────────────────────────────────── */
if ( ! wc_attribute_taxonomy_id_by_name( 'colore' ) ) {
	wc_create_attribute( array( 'name' => 'Colore', 'slug' => 'colore', 'type' => 'select', 'order_by' => 'menu_order', 'has_archives' => false ) );
	delete_transient( 'wc_attribute_taxonomies' );
	WC_Cache_Helper::invalidate_cache_group( 'woocommerce-attributes' );
}
if ( ! taxonomy_exists( 'pa_colore' ) ) {
	register_taxonomy( 'pa_colore', array( 'product' ), array( 'hierarchical' => false ) );
}

/* ── Copy helpers ───────────────────────────────────────────────────── */
function pishop_description( $p, $cat_name ) {
	$specs = '';
	foreach ( $p['specs'] as $k => $v ) {
		$specs .= '<tr><th>' . esc_html( $k ) . '</th><td>' . esc_html( $v ) . '</td></tr>';
	}
	$first = array_values( $p['specs'] );
	$keys  = array_keys( $p['specs'] );
	return '<h2>Panoramica</h2>'
		. '<p>' . esc_html( $p['short'] ) . ' ' . esc_html( $p['name'] ) . ' è una delle scelte più apprezzate nella categoria ' . esc_html( $cat_name ) . ' su PiShop: qualità del marchio ' . esc_html( $p['brand'] ) . ', garanzia ufficiale Italia di 24 mesi e assistenza dedicata.</p>'
		. '<h2>Design e qualità costruttiva</h2>'
		. '<p>Materiali curati, finiture precise ed ergonomia studiata per l’uso quotidiano. Leggero da portare con sé, solido quando serve.</p>'
		. '<h2>Prestazioni</h2>'
		. '<p>' . esc_html( $keys[0] ?? '' ) . ': <strong>' . esc_html( $first[0] ?? '' ) . '</strong>' . ( isset( $first[1] ) ? ' · ' . esc_html( $keys[1] ) . ': <strong>' . esc_html( $first[1] ) . '</strong>' : '' ) . '. Prestazioni fluide in ogni situazione, dal lavoro allo svago.</p>'
		. '<h2>Specifiche tecniche</h2><table class="pishop-specs"><tbody>' . $specs . '</tbody></table>'
		. '<h2>Perché acquistarlo su PiShop</h2><ul><li>Spedizione gratuita sopra 49 €</li><li>Reso gratuito entro 14 giorni</li><li>Pagamenti sicuri e possibilità di pagare alla consegna</li><li>Prodotto originale con garanzia Italia</li></ul>';
}

$reviewers = array( 'Giulia R.', 'Marco B.', 'Francesca L.', 'Luca M.', 'Sara P.', 'Alessandro T.', 'Chiara D.', 'Davide G.', 'Elena F.', 'Matteo S.' );
$comments  = array(
	5 => array( 'Prodotto eccellente, arrivato in 24 ore e ben imballato. Consigliatissimo!', 'Qualità top, esattamente come descritto. Tornerò a comprare su PiShop.', 'Ottimo rapporto qualità-prezzo, sono molto soddisfatto.' ),
	4 => array( 'Molto buono, unica pecca la confezione un po’ essenziale.', 'Fa il suo lavoro alla grande, spedizione velocissima.', 'Buon acquisto, assistenza clienti gentile e rapida.' ),
	3 => array( 'Discreto, mi aspettavo qualcosa in più sull’autonomia.', 'Nella media, ma il prezzo in offerta lo rende interessante.' ),
);

/* ── Products ───────────────────────────────────────────────────────── */
$created = 0;
$cat_names = array_column( $catalog['categories'], 'name', 'slug' );
foreach ( $catalog['products'] as $n => $p ) {
	$sku   = $p['sku'];
	$pid   = wc_get_product_id_by_sku( $sku );
	$is_var = ! empty( $p['variable'] );
	$is_ext = ! empty( $p['external'] );

	if ( $pid ) {
		$product = wc_get_product( $pid );
	} elseif ( $is_var ) {
		$product = new WC_Product_Variable();
	} elseif ( $is_ext ) {
		$product = new WC_Product_External();
	} else {
		$product = new WC_Product_Simple();
	}

	$product->set_name( $p['name'] );
	$product->set_slug( sanitize_title( $p['name'] ) );
	$product->set_sku( $sku );
	$product->set_status( 'publish' );
	$product->set_catalog_visibility( 'visible' );
	$product->set_short_description( '<p>' . esc_html( $p['short'] ) . '</p>' );
	$product->set_description( pishop_description( $p, $cat_names[ $p['cat'] ] ) );
	$product->set_category_ids( array( $cat_ids[ $p['cat'] ] ) );
	$product->set_featured( ! empty( $p['featured'] ) );
	$product->set_reviews_allowed( true );
	$product->set_menu_order( $n );

	$tags = array();
	foreach ( $p['tags'] as $t ) {
		$tags[] = $tag_map[ $t ];
	}
	if ( ! empty( $p['sale_days'] ) ) {
		$tags[] = $tag_map['lampo'];
	}
	$product->set_tag_ids( $tags );

	// Main image + gallery (colour variants).
	$img = pishop_media( "$root/assets/images/products/" . strtolower( $sku ) . '.jpg', $p['name'] );
	$product->set_image_id( $img );

	// Attributes: global "Colore" (variations) + local spec attributes.
	$attrs = array();
	$pos   = 0;
	$color_terms = array();
	if ( $is_var ) {
		foreach ( array_keys( $p['variable']['Colore'] ) as $cname ) {
			$color_terms[ $cname ] = pishop_term( $cname, 'pa_colore' );
		}
		$a = new WC_Product_Attribute();
		$a->set_id( wc_attribute_taxonomy_id_by_name( 'colore' ) );
		$a->set_name( 'pa_colore' );
		$a->set_options( array_values( $color_terms ) );
		$a->set_position( $pos++ );
		$a->set_visible( true );
		$a->set_variation( true );
		$attrs[] = $a;
	}
	foreach ( $p['specs'] as $k => $v ) {
		$a = new WC_Product_Attribute();
		$a->set_name( $k );
		$a->set_options( array( $v ) );
		$a->set_position( $pos++ );
		$a->set_visible( true );
		$a->set_variation( false );
		$attrs[] = $a;
	}
	$product->set_attributes( $attrs );

	$sale_to = ! empty( $p['sale_days'] ) ? gmdate( 'Y-m-d 23:59:59', strtotime( '+' . (int) $p['sale_days'] . ' days' ) ) : null;

	if ( $is_ext ) {
		$product->set_product_url( $p['external'] );
		$product->set_button_text( 'Acquista sul sito del produttore' );
		$product->set_regular_price( $p['price'] );
	} elseif ( ! $is_var ) {
		$product->set_regular_price( $p['price'] );
		$product->set_sale_price( isset( $p['sale'] ) ? $p['sale'] : '' );
		$product->set_date_on_sale_to( $sale_to );
		$product->set_manage_stock( true );
		$product->set_stock_quantity( $p['stock'] );
		$product->set_stock_status( $p['stock'] > 0 ? 'instock' : 'outofstock' );
		$product->set_low_stock_amount( 5 );
	}
	$product->set_weight( '0.5' );
	$pid = $product->save();

	if ( $brand_ids[ $p['brand'] ] ?? 0 ) {
		wp_set_object_terms( $pid, array( $brand_ids[ $p['brand'] ] ), 'product_brand' );
	}

	// Variations.
	if ( $is_var ) {
		$gallery = array();
		$existing = array();
		foreach ( $product->get_children() as $vid ) {
			$v = wc_get_product( $vid );
			$existing[ $v->get_attribute( 'pa_colore' ) ] = $v;
		}
		$i = 0;
		foreach ( $p['variable']['Colore'] as $cname => $hex ) {
			$term   = get_term( $color_terms[ $cname ], 'pa_colore' );
			$v      = $existing[ $cname ] ?? new WC_Product_Variation();
			$v->set_parent_id( $pid );
			$v->set_attributes( array( 'pa_colore' => $term->slug ) );
			$v->set_sku( $sku . '-' . strtoupper( substr( $term->slug, 0, 3 ) ) );
			$v->set_regular_price( $p['price'] );
			$v->set_sale_price( isset( $p['sale'] ) ? $p['sale'] : '' );
			$v->set_manage_stock( true );
			$v->set_stock_quantity( max( 0, (int) ( $p['stock'] / count( $p['variable']['Colore'] ) ) - $i ) );
			$vimg = pishop_media( "$root/assets/images/products/" . strtolower( $sku ) . '-' . $term->slug . '.jpg', $p['name'] . ' – ' . $cname );
			$v->set_image_id( $vimg );
			$v->set_menu_order( $i++ );
			$v->save();
			$gallery[] = $vimg;
		}
		$product = wc_get_product( $pid );
		$product->set_gallery_image_ids( $gallery );
		$product->set_default_attributes( array( 'pa_colore' => get_term( reset( $color_terms ), 'pa_colore' )->slug ) );
		$product->save();
		WC_Product_Variable::sync( $pid );
	}

	// Sales counter (for "Più venduti" sorting).
	update_post_meta( $pid, 'total_sales', in_array( 'bestseller', $p['tags'], true ) ? 120 + ( $n * 7 ) % 90 : ( $n * 13 ) % 40 );

	// Reviews (only once).
	if ( ! get_comments( array( 'post_id' => $pid, 'count' => true ) ) ) {
		$avg   = (float) $p['rating'];
		$count = 2 + ( $n % 3 );
		for ( $r = 0; $r < $count; $r++ ) {
			$stars = (int) max( 3, min( 5, round( $avg + ( ( $r % 2 ) ? -0.6 : 0.4 ) ) ) );
			$cid   = wp_insert_comment( array(
				'comment_post_ID'      => $pid,
				'comment_author'       => $reviewers[ ( $n + $r ) % count( $reviewers ) ],
				'comment_author_email' => 'cliente' . ( $n * 10 + $r ) . '@example.com',
				'comment_content'      => $comments[ $stars ][ ( $n + $r ) % count( $comments[ $stars ] ) ],
				'comment_type'         => 'review',
				'comment_approved'     => 1,
				'comment_date'         => gmdate( 'Y-m-d H:i:s', strtotime( '-' . ( 3 + $n + $r * 5 ) . ' days' ) ),
			) );
			update_comment_meta( $cid, 'rating', $stars );
			update_comment_meta( $cid, 'verified', 1 );
		}
		WC_Comments::clear_transients( $pid );
	}
	++$created;
}
wc_delete_product_transients();
WP_CLI::success( "Products imported/updated: $created" );
