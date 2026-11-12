<?php
/**
 * PiShop – apply Elementor kit, forms, blog posts, pages, header/footer and menus (idempotent).
 *
 * Run: python3 -I scripts/build_pages.py "$PWD" && bin/wp eval-file scripts/apply-pages.php
 */
defined( 'ABSPATH' ) || exit;

$root  = dirname( __DIR__ );
$site  = json_decode( file_get_contents( "$root/data/build/site.json" ), true );
$media = json_decode( file_get_contents( "$root/data/media-map.json" ), true );

/* ── 1. Elementor kit: global colours & fonts ───────────────────────── */
$kit_id   = (int) get_option( 'elementor_active_kit' );
$settings = get_post_meta( $kit_id, '_elementor_page_settings', true );
$settings = is_array( $settings ) ? $settings : array();
$settings['system_colors'] = array(
	array( '_id' => 'primary', 'title' => 'Arancione PiShop', 'color' => '#FF6A00' ),
	array( '_id' => 'secondary', 'title' => 'Nero', 'color' => '#111111' ),
	array( '_id' => 'text', 'title' => 'Testo', 'color' => '#2B2B2B' ),
	array( '_id' => 'accent', 'title' => 'Grigio', 'color' => '#6B7280' ),
);
$settings['custom_colors'] = array(
	array( '_id' => 'pi_white', 'title' => 'Bianco', 'color' => '#FFFFFF' ),
	array( '_id' => 'pi_gray100', 'title' => 'Grigio chiaro', 'color' => '#F4F5F7' ),
	array( '_id' => 'pi_gray200', 'title' => 'Grigio bordo', 'color' => '#E5E7EB' ),
	array( '_id' => 'pi_orange_light', 'title' => 'Arancione chiaro', 'color' => '#FFF1E6' ),
	array( '_id' => 'pi_orange_dark', 'title' => 'Arancione scuro', 'color' => '#E05A00' ),
);
$font = function ( $id, $title, $family, $weight, $size = null ) {
	$f = array( '_id' => $id, 'title' => $title, 'typography_typography' => 'custom', 'typography_font_family' => $family, 'typography_font_weight' => (string) $weight );
	if ( $size ) {
		$f['typography_font_size'] = array( 'unit' => 'px', 'size' => $size );
	}
	return $f;
};
$settings['system_typography'] = array(
	$font( 'primary', 'Titoli', 'Poppins', 700 ),
	$font( 'secondary', 'Sottotitoli', 'Poppins', 600 ),
	$font( 'text', 'Testo', 'Inter', 400, 16 ),
	$font( 'accent', 'Accento', 'Inter', 600 ),
);
$settings['container_width']        = array( 'unit' => 'px', 'size' => 1280 );
$settings['space_between_widgets']  = array( 'column' => '16', 'row' => '16', 'isLinked' => true, 'unit' => 'px', 'size' => 16 );
$settings['site_name']              = 'PiShop';
$settings['body_background_background'] = 'classic';
$settings['body_background_color']  = '#FFFFFF';
$settings['button_typography_typography']  = 'custom';
$settings['button_typography_font_family'] = 'Poppins';
$settings['button_typography_font_weight'] = '600';
$settings['button_background_color']       = '#FF6A00';
$settings['button_border_radius']          = array( 'unit' => 'px', 'top' => '999', 'right' => '999', 'bottom' => '999', 'left' => '999', 'isLinked' => true );
update_post_meta( $kit_id, '_elementor_page_settings', $settings );
update_option( 'elementor_disable_color_schemes', 'yes' );
update_option( 'elementor_disable_typography_schemes', 'yes' );
update_option( 'elementor_cpt_support', array( 'page', 'post', 'elementor-hf' ) );
update_option( 'elementor_load_fa4_shim', '' );
WP_CLI::log( 'Kit updated' );

/* ── 2. WPForms: contact + newsletter ───────────────────────────────── */
function pishop_form( $title, $fields, $submit, $confirm ) {
	$existing = get_posts( array( 'post_type' => 'wpforms', 'title' => $title, 'post_status' => 'any', 'numberposts' => 1, 'fields' => 'ids' ) );
	$id       = $existing ? (int) $existing[0] : (int) wp_insert_post( array( 'post_type' => 'wpforms', 'post_status' => 'publish', 'post_title' => $title ) );
	$data     = array(
		'id'       => $id,
		'field_id' => count( $fields ) + 1,
		'fields'   => $fields,
		'settings' => array(
			'form_title'             => $title,
			'submit_text'            => $submit,
			'submit_text_processing' => 'Invio in corso…',
			'antispam_v3'            => '1',
			'notification_enable'    => '1',
			'notifications'          => array( 1 => array( 'email' => '{admin_email}', 'subject' => "Nuovo messaggio: $title", 'sender_name' => 'PiShop', 'sender_address' => '{admin_email}', 'message' => '{all_fields}' ) ),
			'confirmations'          => array( 1 => array( 'type' => 'message', 'message' => "<p>$confirm</p>", 'message_scroll' => '1' ) ),
		),
	);
	wp_update_post( array( 'ID' => $id, 'post_content' => wp_slash( wp_json_encode( $data ) ) ) );
	return $id;
}
$f_contact = pishop_form(
	'Contatti PiShop',
	array(
		1 => array( 'id' => '1', 'type' => 'name', 'label' => 'Nome e cognome', 'format' => 'simple', 'required' => '1', 'size' => 'large' ),
		2 => array( 'id' => '2', 'type' => 'email', 'label' => 'Email', 'required' => '1', 'size' => 'large' ),
		3 => array( 'id' => '3', 'type' => 'select', 'label' => 'Argomento', 'choices' => array( 1 => array( 'label' => 'Informazioni su un prodotto' ), 2 => array( 'label' => 'Stato di un ordine' ), 3 => array( 'label' => 'Resi e rimborsi' ), 4 => array( 'label' => 'Altro' ) ), 'size' => 'large' ),
		4 => array( 'id' => '4', 'type' => 'text', 'label' => 'Numero d’ordine (facoltativo)', 'size' => 'large' ),
		5 => array( 'id' => '5', 'type' => 'textarea', 'label' => 'Messaggio', 'required' => '1', 'size' => 'medium' ),
		6 => array( 'id' => '6', 'type' => 'checkbox', 'label' => 'Privacy', 'required' => '1', 'choices' => array( 1 => array( 'label' => 'Ho letto la Privacy Policy e acconsento al trattamento dei dati.' ) ) ),
	),
	'Invia messaggio',
	'Grazie! Abbiamo ricevuto il tuo messaggio e ti risponderemo entro 24 ore lavorative.'
);
$f_news = pishop_form(
	'Newsletter PiShop',
	array( 1 => array( 'id' => '1', 'type' => 'email', 'label' => 'La tua email', 'label_hide' => '1', 'placeholder' => 'La tua email', 'required' => '1', 'size' => 'large' ) ),
	'Iscriviti',
	'Iscrizione completata! Controlla la tua email per il coupon di benvenuto.'
);
$GLOBALS['f_contact'] = $f_contact; // eval-file runs in function scope
$GLOBALS['f_news']    = $f_news;
WP_CLI::log( "Forms: contact=$f_contact newsletter=$f_news" );

/* ── 3. Blog posts ──────────────────────────────────────────────────── */
wp_update_term( 1, 'category', array( 'name' => 'Notizie', 'slug' => 'notizie' ) );
foreach ( json_decode( file_get_contents( "$root/data/posts.json" ), true ) as $p ) {
	$cat     = term_exists( $p['category'], 'category' );
	$cat_id  = $cat ? (int) $cat['term_id'] : (int) wp_insert_term( $p['category'], 'category' )['term_id'];
	$found   = get_page_by_path( $p['slug'], OBJECT, 'post' );
	$postarr = array(
		'post_type'     => 'post',
		'post_status'   => 'publish',
		'post_title'    => $p['title'],
		'post_name'     => $p['slug'],
		'post_content'  => $p['content'],
		'post_excerpt'  => $p['excerpt'],
		'post_category' => array( $cat_id ),
		'post_date'     => gmdate( 'Y-m-d H:i:s', strtotime( '-' . (int) $p['days_ago'] . ' days 10:00' ) ),
		'post_author'   => 1,
	);
	if ( $found ) {
		$postarr['ID'] = $found->ID;
	}
	$pid = wp_insert_post( wp_slash( $postarr ) );
	set_post_thumbnail( $pid, $media[ $p['photo'] ]['id'] );
}
WP_CLI::log( 'Blog posts ready' );

/* ── 4. Elementor documents ─────────────────────────────────────────── */
function pishop_elementor_save( $post_id, $data, $doc_type, $template ) {
	$json = wp_json_encode( $data );
	$json = str_replace( array( '{{FORM_CONTACT}}', '{{FORM_NEWSLETTER}}' ), array( $GLOBALS['f_contact'], $GLOBALS['f_news'] ), $json );
	update_post_meta( $post_id, '_elementor_edit_mode', 'builder' );
	update_post_meta( $post_id, '_elementor_template_type', $doc_type );
	update_post_meta( $post_id, '_elementor_version', ELEMENTOR_VERSION );
	update_post_meta( $post_id, '_elementor_data', wp_slash( $json ) );
	update_post_meta( $post_id, '_wp_page_template', $template );
	delete_post_meta( $post_id, '_elementor_css' );
	delete_post_meta( $post_id, '_elementor_element_cache' );
}

function pishop_find( $slug, $type ) {
	global $wpdb;
	return (int) $wpdb->get_var( $wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_name = %s AND post_type = %s AND post_status <> 'trash' ORDER BY ID ASC LIMIT 1", $slug, $type ) );
}

// Header & footer (Header Footer Elementor).
foreach ( $site['templates'] as $t ) {
	$id = pishop_find( $t['slug'], 'elementor-hf' );
	$id = wp_insert_post( array( 'ID' => $id, 'post_type' => 'elementor-hf', 'post_status' => 'publish', 'post_title' => $t['title'], 'post_name' => $t['slug'] ) );
	update_post_meta( $id, 'ehf_template_type', $t['type'] );
	update_post_meta( $id, 'ehf_target_include_locations', array( 'rule' => array( 'basic-global' ), 'specific' => array() ) );
	update_post_meta( $id, 'ehf_target_exclude_locations', array() );
	update_post_meta( $id, 'ehf_target_user_roles', array( 'all' ) );
	update_post_meta( $id, 'display-on-canvas-template', '1' );
	pishop_elementor_save( $id, $t['data'], 'wp-post', 'elementor_canvas' );
}

// Pages.
$ids = array();
foreach ( $site['pages'] as $p ) {
	$id = pishop_find( $p['slug'], 'page' );
	$id = wp_insert_post(
		array(
			'ID'           => $id,
			'post_type'    => 'page',
			'post_status'  => 'publish',
			'post_title'   => $p['title'],
			'post_name'    => $p['slug'],
			'post_content' => '',
			'comment_status' => 'closed',
		)
	);
	pishop_elementor_save( $id, $p['data'], 'wp-page', 'elementor_header_footer' );
	$ids[ $p['slug'] ] = $id;
	if ( ! empty( $p['front'] ) ) {
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', $id );
	}
	switch ( $p['option'] ?? '' ) {
		case 'woosc':
			$s = (array) get_option( 'woosc_settings', array() );
			$s['page_id'] = $id;
			update_option( 'woosc_settings', $s );
			break;
		case 'woosw':
			update_option( 'woosw_page_id', $id );
			break;
		case '':
			break;
		default:
			update_option( $p['option'], $id );
	}
}
// Remove the plugin-created duplicate wishlist page (slug "wishlist") if ours exists.
$old = pishop_find( 'wishlist', 'page' );
if ( $old && $old !== $ids['lista-desideri'] ) {
	wp_delete_post( $old, true );
}
WP_CLI::log( 'Pages: ' . count( $ids ) );

/* ── 5. Menus ───────────────────────────────────────────────────────── */
$menu_name = 'Menu principale';
$menu      = wp_get_nav_menu_object( 'menu-principale' );
if ( $menu ) {
	foreach ( wp_get_nav_menu_items( $menu->term_id ) as $item ) {
		wp_delete_post( $item->ID, true );
	}
	$menu_id = $menu->term_id;
} else {
	$menu_id = wp_create_nav_menu( $menu_name );
	wp_update_term( $menu_id, 'nav_menu', array( 'slug' => 'menu-principale' ) );
}
$add = function ( $title, $args, $parent = 0 ) use ( $menu_id ) {
	return wp_update_nav_menu_item( $menu_id, 0, array_merge( array( 'menu-item-title' => $title, 'menu-item-status' => 'publish', 'menu-item-parent-id' => $parent ), $args ) );
};
// Categories live in the [pishop_megamenu] (header), not in this menu.
$add( 'Home', array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => $ids['home'] ) );
$add( 'Negozio', array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => (int) get_option( 'woocommerce_shop_page_id' ) ) );
$add( "⚡\u{00A0}Offerte Lampo", array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => $ids['offerte-lampo'] ) );
$add( 'Marchi', array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => $ids['marchi'] ) );
$add( 'Blog', array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => $ids['blog'] ) );
$add( 'Chi siamo', array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => $ids['chi-siamo'] ) );
$add( 'Contatti', array( 'menu-item-type' => 'post_type', 'menu-item-object' => 'page', 'menu-item-object-id' => $ids['contatti'] ) );
set_theme_mod( 'nav_menu_locations', array( 'primary' => $menu_id, 'mobile_menu' => $menu_id ) );

/* ── 6. Astra layout + site identity ───────────────────────────────── */
$astra = (array) get_option( 'astra-settings', array() );
$astra = array_merge(
	$astra,
	array(
		'site-content-layout'              => 'plain-container',
		'ast-site-content-layout'          => 'full-width-container',
		'site-content-style'               => 'unboxed',
		'single-page-ast-content-layout'   => 'full-width-container',
		'archive-product-ast-content-layout' => 'normal-width-container',
		'single-product-ast-content-layout'  => 'normal-width-container',
		'site-sidebar-layout'              => 'no-sidebar',
		'single-page-sidebar-layout'       => 'no-sidebar',
		'woocommerce-sidebar-layout'       => 'left-sidebar',
		'archive-product-sidebar-layout'   => 'left-sidebar',
		'site-sidebar-width'               => 24,
		'single-product-sidebar-layout'    => 'no-sidebar',
		'site-content-width'               => 1320,
		'theme-color'                      => '#FF6A00',
		'link-color'                       => '#FF6A00',
		'text-color'                       => '#2B2B2B',
		'heading-base-color'               => '#111111',
		'button-bg-color'                  => '#FF6A00',
		'button-bg-h-color'                => '#111111',
		'shop-grid'                        => array( 'desktop' => 3, 'tablet' => 3, 'mobile' => 2 ),
		'shop-no-of-products'              => 16,
		'shop-style'                       => 'shop-page-grid-style',
		'shop-product-structure'           => array( 'category', 'title', 'ratings', 'price', 'add_cart' ),
		'single-product-breadcrumb-disable' => false,
		'blog-single-width'                => 'narrow',
	)
);
update_option( 'astra-settings', $astra );
$logo = $media['brand/icon']['id'] ?? 0;
if ( $logo ) {
	update_option( 'site_icon', $logo );
}
update_option( 'woocommerce_placeholder_image', $media['brand/icon']['id'] ?? '' );

/* ── 6b. Compare / wishlist labels (Italian) ───────────────────────── */
$l = (array) get_option( 'woosc_localization', array() );
update_option( 'woosc_localization', array_merge( $l, array( 'button' => 'Confronta', 'button_added' => 'In confronto', 'bar_compare' => 'Confronta', 'bar_clear' => 'Svuota', 'table_empty' => 'Nessun prodotto da confrontare.' ) ) );
$l = (array) get_option( 'woosw_localization', array() );
update_option( 'woosw_localization', array_merge( $l, array( 'button' => 'Preferiti', 'button_added' => 'Nei preferiti', 'popup_heading' => 'Lista desideri', 'empty_message' => 'La tua lista desideri è vuota.' ) ) );

/* ── 6c. Shop sidebar filters (classic Woo widgets) ─────────────────── */
$sidebar = 'astra-woo-shop-sidebar';
$widgets = array(
	'woocommerce_product_categories' => array( 'title' => 'Categorie', 'count' => 1, 'hierarchical' => 1, 'orderby' => 'order' ),
	'woocommerce_price_filter'       => array( 'title' => 'Filtra per prezzo' ),
	'woocommerce_layered_nav'        => array( 'title' => 'Colore', 'attribute' => 'colore', 'display_type' => 'list', 'query_type' => 'or' ),
	'woocommerce_rating_filter'      => array( 'title' => 'Valutazione' ),
);
$sidebars = get_option( 'sidebars_widgets', array() );
$sidebars[ $sidebar ] = array();
foreach ( $widgets as $base => $instance ) {
	$all              = get_option( "widget_$base", array() );
	$all              = is_array( $all ) ? $all : array();
	$all[1]           = $instance;
	$all['_multiwidget'] = 1;
	update_option( "widget_$base", $all );
	$sidebars[ $sidebar ][] = "$base-1";
}
update_option( 'sidebars_widgets', $sidebars );

/* ── 7. Clear caches ────────────────────────────────────────────────── */
if ( class_exists( '\Elementor\Plugin' ) ) {
	\Elementor\Plugin::$instance->files_manager->clear_cache();
}
flush_rewrite_rules( false );
WP_CLI::success( 'Site applied' );
