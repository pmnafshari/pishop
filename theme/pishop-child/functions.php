<?php
/**
 * PiShop child theme bootstrap.
 *
 * @package pishop-child
 */

defined( 'ABSPATH' ) || exit;

define( 'PISHOP_VERSION', '1.0.0' );

/**
 * Styles: parent, Google Fonts, child design system.
 */
function pishop_enqueue_assets() {
	wp_enqueue_style( 'astra-parent', get_template_directory_uri() . '/style.css', array(), PISHOP_VERSION );
	wp_enqueue_style( 'pishop-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700;800&display=swap', array(), null );
	$css = get_stylesheet_directory() . '/assets/css/pishop.css';
	wp_enqueue_style( 'pishop', get_stylesheet_directory_uri() . '/assets/css/pishop.css', array( 'astra-theme-css' ), file_exists( $css ) ? filemtime( $css ) : PISHOP_VERSION );
}
add_action( 'wp_enqueue_scripts', 'pishop_enqueue_assets', 20 );

require_once __DIR__ . '/inc/shop.php';
require_once __DIR__ . '/inc/megamenu.php';
