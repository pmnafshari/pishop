<?php
/**
 * PiShop – import banners, photos and brand assets into the media library (idempotent)
 * and write data/media-map.json ( "folder/file" => {id,url} ) for the page builder.
 *
 * Run: bin/wp eval-file scripts/import-media.php
 */
defined( 'ABSPATH' ) || exit;
require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

$root = dirname( __DIR__ );
$alts = array(
	'hero-smartphone' => 'Smartphone in offerta su PiShop',
	'hero-laptop'     => 'Laptop e cuffie wireless',
	'hero-gaming'     => 'Console e accessori gaming',
	'logo'            => 'PiShop logo',
	'logo-white'      => 'PiShop logo',
	'icon'            => 'PiShop',
);
$map = array();
foreach ( array( 'banners', 'photos', 'brand' ) as $folder ) {
	foreach ( glob( "$root/assets/images/$folder/*.{png,jpg}", GLOB_BRACE ) as $path ) {
		$name  = pathinfo( $path, PATHINFO_FILENAME );
		$key   = 'pishop_src_' . md5( basename( $path ) );
		$found = get_posts( array( 'post_type' => 'attachment', 'meta_key' => '_pishop_src', 'meta_value' => $key, 'fields' => 'ids', 'numberposts' => 1 ) );
		if ( $found ) {
			$id = (int) $found[0];
			// File changed since import? Replace it in place and rebuild thumbnails.
			if ( get_post_meta( $id, '_pishop_hash', true ) !== md5_file( $path ) ) {
				copy( $path, get_attached_file( $id ) );
				wp_update_attachment_metadata( $id, wp_generate_attachment_metadata( $id, get_attached_file( $id ) ) );
				update_post_meta( $id, '_pishop_hash', md5_file( $path ) );
				WP_CLI::log( "refreshed $name" );
			}
		} else {
			$tmp = wp_tempnam( basename( $path ) );
			copy( $path, $tmp );
			$alt = $alts[ $name ] ?? ucfirst( str_replace( '-', ' ', $name ) );
			$id  = media_handle_sideload( array( 'name' => basename( $path ), 'tmp_name' => $tmp ), 0, $alt );
			if ( is_wp_error( $id ) ) {
				WP_CLI::warning( $id->get_error_message() );
				continue;
			}
			update_post_meta( $id, '_pishop_src', $key );
			update_post_meta( $id, '_pishop_hash', md5_file( $path ) );
			update_post_meta( $id, '_wp_attachment_image_alt', $alt );
		}
		$map[ "$folder/$name" ] = array( 'id' => $id, 'url' => wp_get_attachment_url( $id ) );
	}
}
// Category + product images (already imported by import-catalog.php).
foreach ( get_terms( array( 'taxonomy' => 'product_cat', 'hide_empty' => false ) ) as $t ) {
	$tid = (int) get_term_meta( $t->term_id, 'thumbnail_id', true );
	if ( $tid ) {
		$map[ "categories/{$t->slug}" ] = array( 'id' => $tid, 'url' => wp_get_attachment_url( $tid ), 'link' => get_term_link( $t ) );
	}
}
file_put_contents( "$root/data/media-map.json", wp_json_encode( $map, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) );
WP_CLI::success( count( $map ) . ' media entries mapped' );
