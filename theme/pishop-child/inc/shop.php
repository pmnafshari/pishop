<?php
/**
 * PiShop – shortcodes used inside Elementor pages + WooCommerce tweaks.
 *
 * Shortcodes:
 *  [pishop_search]            Product search form (header)
 *  [pishop_header_icons]      Account / wishlist / cart icons with counters
 *  [pishop_countdown]         Countdown to the end of the nearest flash sale
 *  [pishop_flash_products]    Products tagged "offerta-lampo" with stock bar
 *  [pishop_brands]            Brand chips with product counts
 *  [pishop_latest_posts n=3]  Latest blog posts as cards
 *  [pishop_year]              Current year
 *
 * @package pishop-child
 */

defined( 'ABSPATH' ) || exit;

/* ───────────────────────── Icons (inline SVG, no external requests) ── */
function pishop_icon( $name ) {
	$p = array(
		'user'   => '<path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2c-4.4 0-8 2.2-8 5v1h16v-1c0-2.8-3.6-5-8-5Z"/>',
		'heart'  => '<path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 4.5 6.7 4.5c2 0 3.6 1.1 5.3 3 1.7-1.9 3.3-3 5.3-3 3.7 0 5.8 3.9 4.3 7.3C19.5 16.4 12 21 12 21Z"/>',
		'cart'   => '<path d="M3 4h2l2.4 10.2A2 2 0 0 0 9.4 16h8.2a2 2 0 0 0 2-1.6L21 7H6.2"/><circle cx="10" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/>',
		'search' => '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
		'swap'   => '<path d="M7 4 3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7"/>',
	);
	$fill = in_array( $name, array( 'user', 'heart' ), true );
	return '<svg class="pi-ico" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="' . ( $fill ? 'currentColor' : 'none' ) . '" stroke="' . ( $fill ? 'none' : 'currentColor' ) . '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' . $p[ $name ] . '</svg>';
}

/* ───────────────────────── Header ───────────────────────────────────── */
add_shortcode(
	'pishop_search',
	function () {
		$q = get_search_query();
		return '<form role="search" method="get" class="pi-search" action="' . esc_url( home_url( '/' ) ) . '">'
			. '<label class="screen-reader-text" for="pi-s">Cerca prodotti</label>'
			. '<input id="pi-s" type="search" name="s" value="' . esc_attr( $q ) . '" placeholder="Cerca smartphone, laptop, cuffie…" autocomplete="off">'
			. '<input type="hidden" name="post_type" value="product">'
			. '<button type="submit" aria-label="Cerca">' . pishop_icon( 'search' ) . '</button></form>';
	}
);

function pishop_cart_count_html() {
	$n = ( function_exists( 'WC' ) && WC()->cart ) ? WC()->cart->get_cart_contents_count() : 0;
	return '<span class="pi-badge pi-cart-count">' . (int) $n . '</span>';
}

add_shortcode(
	'pishop_header_icons',
	function () {
		$account  = wc_get_page_permalink( 'myaccount' );
		$cart     = wc_get_cart_url();
		$wishlist = home_url( '/lista-desideri/' );
		$compare  = home_url( '/confronta/' );
		$label    = is_user_logged_in() ? 'Il mio account' : 'Accedi';
		return '<div class="pi-hicons">'
			. '<a class="pi-hicon pi-hicon--account" href="' . esc_url( $account ) . '">' . pishop_icon( 'user' ) . '<span class="pi-hlabel">' . esc_html( $label ) . '</span></a>'
			. '<a class="pi-hicon" href="' . esc_url( $compare ) . '" aria-label="Confronta">' . pishop_icon( 'swap' ) . '</a>'
			. '<a class="pi-hicon" href="' . esc_url( $wishlist ) . '" aria-label="Lista desideri">' . pishop_icon( 'heart' ) . '</a>'
			. '<a class="pi-hicon pi-hicon--cart" href="' . esc_url( $cart ) . '" aria-label="Carrello">' . pishop_icon( 'cart' ) . pishop_cart_count_html() . '</a>'
			. '</div>';
	}
);

// Keep the cart counter fresh after AJAX add-to-cart.
add_filter(
	'woocommerce_add_to_cart_fragments',
	function ( $fragments ) {
		$fragments['span.pi-cart-count'] = pishop_cart_count_html();
		return $fragments;
	}
);

/* ───────────────────────── Flash deals ─────────────────────────────── */
function pishop_flash_query_ids() {
	return wc_get_products(
		array(
			'status'   => 'publish',
			'limit'    => 8,
			'tag'      => array( 'offerta-lampo' ),
			'orderby'  => 'menu_order',
			'order'    => 'ASC',
			'return'   => 'ids',
		)
	);
}

add_shortcode(
	'pishop_countdown',
	function ( $atts ) {
		$atts = shortcode_atts( array( 'label' => 'L’offerta termina tra' ), $atts );
		$end  = 0;
		foreach ( pishop_flash_query_ids() as $id ) {
			$p  = wc_get_product( $id );
			$to = $p ? $p->get_date_on_sale_to() : null;
			if ( $to && $to->getTimestamp() > time() && ( ! $end || $to->getTimestamp() < $end ) ) {
				$end = $to->getTimestamp();
			}
		}
		if ( ! $end ) {
			$end = strtotime( 'tomorrow 23:59:59' );
		}
		$box = function ( $k, $l ) {
			return '<span class="pi-cd__box"><b data-k="' . $k . '">00</b><small>' . $l . '</small></span>';
		};
		return '<div class="pi-cd" data-end="' . (int) $end . '"><span class="pi-cd__label">' . esc_html( $atts['label'] ) . '</span>'
			. $box( 'd', 'giorni' ) . $box( 'h', 'ore' ) . $box( 'm', 'min' ) . $box( 's', 'sec' ) . '</div>';
	}
);

add_shortcode(
	'pishop_flash_products',
	function ( $atts ) {
		$atts = shortcode_atts( array( 'columns' => 4, 'limit' => 8 ), $atts );
		$ids  = array_slice( pishop_flash_query_ids(), 0, (int) $atts['limit'] );
		if ( ! $ids ) {
			return '<p>Nessuna offerta lampo attiva in questo momento.</p>';
		}
		return do_shortcode( '[products ids="' . implode( ',', $ids ) . '" columns="' . (int) $atts['columns'] . '" orderby="post__in" class="pi-flash"]' );
	}
);

// Stock progress bar on flash-sale cards.
add_action(
	'astra_woo_shop_price_after',
	function () {
		global $product;
		if ( ! $product || ! has_term( 'offerta-lampo', 'product_tag', $product->get_id() ) || ! $product->managing_stock() ) {
			return;
		}
		$left = max( 0, (int) $product->get_stock_quantity() );
		$sold = (int) $product->get_total_sales();
		$pct  = $left + $sold ? round( $sold / ( $left + $sold ) * 100 ) : 0;
		echo '<div class="pi-stock"><div class="pi-stockbar"><span style="width:' . (int) $pct . '%"></span></div><p class="pi-stocktext">Disponibili: <b>' . (int) $left . '</b> · Venduti: ' . (int) $sold . '</p></div>';
	}
);

/* ───────────────────────── Brands & blog ───────────────────────────── */
add_shortcode(
	'pishop_brands',
	function () {
		$terms = get_terms( array( 'taxonomy' => 'product_brand', 'hide_empty' => true ) );
		if ( is_wp_error( $terms ) || ! $terms ) {
			return '';
		}
		$out = '<ul class="pi-brands">';
		foreach ( $terms as $t ) {
			$out .= '<li><a href="' . esc_url( get_term_link( $t ) ) . '"><span class="pi-brands__name">' . esc_html( $t->name ) . '</span><span class="pi-brands__count">' . (int) $t->count . ' prodott' . ( 1 === (int) $t->count ? 'o' : 'i' ) . '</span></a></li>';
		}
		return $out . '</ul>';
	}
);

add_shortcode(
	'pishop_latest_posts',
	function ( $atts ) {
		$atts  = shortcode_atts( array( 'n' => 3, 'offset' => 0 ), $atts );
		$posts = get_posts( array( 'numberposts' => (int) $atts['n'], 'offset' => (int) $atts['offset'], 'post_status' => 'publish' ) );
		$out   = '<div class="pi-posts">';
		foreach ( $posts as $p ) {
			$cat  = get_the_category( $p->ID );
			$out .= '<article class="pi-post"><a class="pi-post__img" href="' . esc_url( get_permalink( $p ) ) . '">' . get_the_post_thumbnail( $p, 'medium_large', array( 'loading' => 'lazy' ) ) . '</a>'
				. '<div class="pi-post__body">' . ( $cat ? '<span class="pi-post__cat">' . esc_html( $cat[0]->name ) . '</span>' : '' )
				. '<h3><a href="' . esc_url( get_permalink( $p ) ) . '">' . esc_html( get_the_title( $p ) ) . '</a></h3>'
				. '<p>' . esc_html( wp_trim_words( get_the_excerpt( $p ), 20 ) ) . '</p>'
				. '<span class="pi-post__meta">' . esc_html( get_the_date( 'j F Y', $p ) ) . ' · ' . max( 1, (int) ceil( count( preg_split( '/\\s+/u', wp_strip_all_tags( $p->post_content ), -1, PREG_SPLIT_NO_EMPTY ) ) / 200 ) ) . ' min di lettura</span></div></article>';
		}
		return $out . '</div>';
	}
);

add_shortcode( 'pishop_year', fn() => gmdate( 'Y' ) );

/* ───────────────────────── WooCommerce tweaks ──────────────────────── */
// Percentage sale badge ("-15%").
add_filter(
	'woocommerce_sale_flash',
	function ( $html, $post, $product ) {
		$reg  = (float) $product->get_regular_price();
		$sale = (float) $product->get_sale_price();
		if ( $product->is_type( 'variable' ) ) {
			$reg  = (float) $product->get_variation_regular_price( 'max' );
			$sale = (float) $product->get_variation_sale_price( 'min' );
		}
		if ( $reg > 0 && $sale > 0 && $sale < $reg ) {
			return '<span class="onsale">-' . round( ( $reg - $sale ) / $reg * 100 ) . '%</span>';
		}
		return $html;
	},
	20, // After Astra's own sale_flash filter (priority 10).
	3
);

// "Novità" badge.
add_action(
	'woocommerce_before_shop_loop_item_title',
	function () {
		global $product;
		if ( $product && has_term( 'novita', 'product_tag', $product->get_id() ) ) {
			echo '<span class="pi-new">Novità</span>';
		}
	},
	9
);

// Free-shipping progress in cart & mini-cart.
function pishop_free_shipping_notice() {
	if ( ! WC()->cart ) {
		return;
	}
	$min   = 49;
	$total = (float) WC()->cart->get_displayed_subtotal();
	$pct   = min( 100, round( $total / $min * 100 ) );
	$msg   = $total >= $min ? 'Complimenti! Hai diritto alla <b>spedizione gratuita</b>.' : 'Ti mancano <b>' . wc_price( $min - $total ) . '</b> per la spedizione gratuita.';
	echo '<div class="pi-freeship"><p>' . wp_kses_post( $msg ) . '</p><div class="pi-stockbar"><span style="width:' . (int) $pct . '%"></span></div></div>';
}
add_action( 'woocommerce_before_cart', 'pishop_free_shipping_notice' );
add_action( 'woocommerce_before_checkout_form', 'pishop_free_shipping_notice', 5 );

// Trust row under the add-to-cart button.
add_action(
	'woocommerce_single_product_summary',
	function () {
		echo '<ul class="pi-trust"><li>🚚 Spedizione gratuita sopra 49 €</li><li>↩️ Reso gratuito entro 14 giorni</li><li>🛡️ Garanzia Italia 24 mesi</li><li>🔒 Pagamenti sicuri</li></ul>';
	},
	35
);

// 4 related products, 4 columns.
add_filter(
	'woocommerce_output_related_products_args',
	function ( $args ) {
		$args['posts_per_page'] = 4;
		$args['columns']        = 4;
		return $args;
	}
);
add_filter( 'loop_shop_per_page', fn() => 16, 20 );

// Rename the reviews tab and Italianise a few labels.
add_filter(
	'woocommerce_product_tabs',
	function ( $tabs ) {
		if ( isset( $tabs['description'] ) ) {
			$tabs['description']['title'] = 'Descrizione';
		}
		if ( isset( $tabs['additional_information'] ) ) {
			$tabs['additional_information']['title'] = 'Scheda tecnica';
		}
		return $tabs;
	},
	98
);

/* ───────────────────────── Front-end JS (countdown) ────────────────── */
add_action(
	'wp_footer',
	function () {
		?>
<script>
(function(){document.querySelectorAll('.pi-cd').forEach(function(el){var end=+el.dataset.end*1000;function p(n){return String(n).padStart(2,'0')}function t(){var d=Math.max(0,end-Date.now())/1000;var v={d:Math.floor(d/86400),h:Math.floor(d%86400/3600),m:Math.floor(d%3600/60),s:Math.floor(d%60)};for(var k in v){var b=el.querySelector('[data-k="'+k+'"]');if(b)b.textContent=p(v[k]);}}t();setInterval(t,1000);});})();
</script>
		<?php
	},
	99
);

// When free shipping is available, hide the paid flat rate (keep pickup).
add_filter(
	'woocommerce_package_rates',
	function ( $rates ) {
		$free = array_filter( $rates, fn( $r ) => 'free_shipping' === $r->method_id );
		if ( ! $free ) {
			return $rates;
		}
		return array_filter( $rates, fn( $r ) => 'flat_rate' !== $r->method_id );
	},
	100
);

// Featured image at the top of single blog posts.
add_action(
	'astra_entry_content_before',
	function () {
		if ( is_singular( 'post' ) && has_post_thumbnail() ) {
			echo '<figure class="pi-post-hero">' . get_the_post_thumbnail( null, 'large', array( 'loading' => 'eager' ) ) . '</figure>';
		}
	}
);
