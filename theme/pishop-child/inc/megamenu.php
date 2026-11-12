<?php
/**
 * PiShop mega menu – [pishop_megamenu]
 *
 * Pattern adapted from the iShop reference: a "Categorie" trigger opens a panel with
 * parent categories on the left (icon + name) and, on hover, a pane on the right with
 * grouped links. PiShop version: emoji icons, brand/price/discover groups that link to
 * real filtered results, and a best-seller card per category.
 * Desktop: hover/click panel + dimmed page layer. Mobile: slide-in drawer with drill-down.
 *
 * @package pishop-child
 */

defined( 'ABSPATH' ) || exit;

/**
 * Data for the menu: one entry per top-level product category.
 */
function pishop_megamenu_data() {
	$cached = get_transient( 'pishop_megamenu_v1' );
	if ( is_array( $cached ) ) {
		return $cached;
	}
	$terms = get_terms(
		array(
			'taxonomy'   => 'product_cat',
			'hide_empty' => true,
			'parent'     => 0,
			'meta_key'   => 'order',
			'orderby'    => 'meta_value_num',
			'order'      => 'ASC',
			'exclude'    => array( (int) get_option( 'default_product_cat' ) ),
		)
	);
	$out = array();
	foreach ( (array) $terms as $t ) {
		$url = get_term_link( $t );
		$ids = wc_get_products( array( 'status' => 'publish', 'limit' => -1, 'category' => array( $t->slug ), 'return' => 'ids' ) );

		// Brands present in this category.
		$brands = wp_get_object_terms( $ids, 'product_brand', array( 'orderby' => 'name' ) );
		$brand_links = array();
		foreach ( is_wp_error( $brands ) ? array() : $brands as $b ) {
			$brand_links[ $b->slug ] = array( $b->name, add_query_arg( 'product_brand', $b->slug, $url ) );
		}

		// Price buckets from the real price range of the category.
		$prices = array();
		foreach ( $ids as $id ) {
			$p = wc_get_product( $id );
			if ( $p && '' !== $p->get_price() ) {
				$prices[] = (float) $p->get_price();
			}
		}
		$buckets = array();
		if ( $prices ) {
			$min   = min( $prices );
			$max   = max( $prices );
			$steps = array( 50, 100, 300, 500, 1000, 1500 );
			$cuts  = array_values( array_filter( $steps, fn( $s ) => $s > $min && $s < $max ) );
			$cuts  = array_slice( $cuts, 0, 3 );
			$prev  = 0;
			foreach ( $cuts as $c ) {
				$buckets[] = array( $prev ? sprintf( '%d – %d €', $prev, $c ) : sprintf( 'Fino a %d €', $c ), add_query_arg( array( 'min_price' => $prev, 'max_price' => $c ), $url ) );
				$prev      = $c;
			}
			$buckets[] = array( $prev ? sprintf( 'Oltre %d €', $prev ) : 'Tutti i prezzi', add_query_arg( array( 'min_price' => $prev, 'max_price' => (int) ceil( $max ) ), $url ) );
		}

		// Best seller of the category.
		$best = wc_get_products( array( 'status' => 'publish', 'limit' => 1, 'category' => array( $t->slug ), 'orderby' => 'popularity', 'order' => 'DESC', 'stock_status' => 'instock' ) );
		$card = null;
		if ( $best ) {
			$b    = $best[0];
			$card = array(
				'name'  => $b->get_name(),
				'url'   => $b->get_permalink(),
				'img'   => wp_get_attachment_image_url( $b->get_image_id(), 'woocommerce_thumbnail' ),
				'price' => $b->get_price_html(),
				'sale'  => $b->is_on_sale(),
			);
		}

		$out[] = array(
			'slug'    => $t->slug,
			'name'    => $t->name,
			'emoji'   => get_term_meta( $t->term_id, 'pishop_emoji', true ) ?: '🛍️',
			'url'     => $url,
			'count'   => count( $ids ),
			'desc'    => $t->description,
			'brands'  => array_values( $brand_links ),
			'prices'  => $buckets,
			'discover' => array(
				array( '✨ Novità', add_query_arg( 'orderby', 'date', $url ) ),
				array( '🔥 Più venduti', add_query_arg( 'orderby', 'popularity', $url ) ),
				array( '⭐ Migliori valutazioni', add_query_arg( 'orderby', 'rating', $url ) ),
				array( '💸 Prezzo crescente', add_query_arg( 'orderby', 'price', $url ) ),
			),
			'card'    => $card,
		);
	}
	set_transient( 'pishop_megamenu_v1', $out, DAY_IN_SECONDS );
	return $out;
}

// Rebuild the cached menu whenever products or categories change.
foreach ( array( 'woocommerce_update_product', 'woocommerce_new_product', 'edited_product_cat', 'created_product_cat', 'delete_product_cat', 'woocommerce_product_set_stock' ) as $hook ) {
	add_action( $hook, fn() => delete_transient( 'pishop_megamenu_v1' ) );
}

add_shortcode(
	'pishop_megamenu',
	function () {
		$cats = pishop_megamenu_data();
		if ( ! $cats ) {
			return '';
		}
		ob_start();
		?>
<div class="pi-mm" data-pi-mm>
	<button type="button" class="pi-mm__trigger" aria-expanded="false" aria-controls="pi-mm-panel">
		<span class="pi-mm__burger" aria-hidden="true"><i></i><i></i><i></i></span>
		<span>Categorie</span>
		<svg class="pi-mm__chev" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
	</button>
	<div class="pi-mm__panel" id="pi-mm-panel" role="dialog" aria-label="Categorie prodotti">
		<div class="pi-mm__head">
			<button type="button" class="pi-mm__back" aria-label="Torna alle categorie">←</button>
			<strong class="pi-mm__title">🛍️ Tutte le categorie</strong>
			<button type="button" class="pi-mm__close" aria-label="Chiudi">✕</button>
		</div>
		<div class="pi-mm__wrap">
			<ul class="pi-mm__cats" role="list">
				<?php foreach ( $cats as $i => $c ) : ?>
				<li>
					<a href="<?php echo esc_url( $c['url'] ); ?>" class="pi-mm__cat<?php echo 0 === $i ? ' is-active' : ''; ?>" data-pane="<?php echo esc_attr( $c['slug'] ); ?>" data-title="<?php echo esc_attr( $c['emoji'] . ' ' . $c['name'] ); ?>">
						<span class="pi-mm__emoji" aria-hidden="true"><?php echo esc_html( $c['emoji'] ); ?></span>
						<span class="pi-mm__name"><?php echo esc_html( $c['name'] ); ?><small><?php echo (int) $c['count']; ?> prodotti</small></span>
						<span class="pi-mm__arrow" aria-hidden="true">›</span>
					</a>
				</li>
				<?php endforeach; ?>
				<li class="pi-mm__extra">
					<a href="<?php echo esc_url( home_url( '/offerte-lampo/' ) ); ?>" class="pi-mm__deal">⚡ Offerte Lampo <span>fino al -50%</span></a>
				</li>
			</ul>
			<div class="pi-mm__panes">
				<?php foreach ( $cats as $i => $c ) : ?>
				<section class="pi-mm__pane<?php echo 0 === $i ? ' is-active' : ''; ?>" data-pane="<?php echo esc_attr( $c['slug'] ); ?>" aria-label="<?php echo esc_attr( $c['name'] ); ?>">
					<header class="pi-mm__pane-head">
						<div>
							<h3><span aria-hidden="true"><?php echo esc_html( $c['emoji'] ); ?></span> <?php echo esc_html( $c['name'] ); ?></h3>
							<?php if ( $c['desc'] ) : ?><p><?php echo esc_html( $c['desc'] ); ?></p><?php endif; ?>
						</div>
						<a class="pi-mm__all" href="<?php echo esc_url( $c['url'] ); ?>">Vedi tutti i <?php echo (int) $c['count']; ?> prodotti →</a>
					</header>
					<div class="pi-mm__grid">
						<div class="pi-mm__group">
							<h4>🏷️ Marchi</h4>
							<ul>
								<?php foreach ( $c['brands'] as $b ) : ?>
								<li><a href="<?php echo esc_url( $b[1] ); ?>"><?php echo esc_html( $b[0] ); ?></a></li>
								<?php endforeach; ?>
							</ul>
						</div>
						<div class="pi-mm__group">
							<h4>💶 Fascia di prezzo</h4>
							<ul>
								<?php foreach ( $c['prices'] as $p ) : ?>
								<li><a href="<?php echo esc_url( $p[1] ); ?>"><?php echo esc_html( $p[0] ); ?></a></li>
								<?php endforeach; ?>
							</ul>
						</div>
						<div class="pi-mm__group">
							<h4>🔎 Scopri</h4>
							<ul>
								<?php foreach ( $c['discover'] as $d ) : ?>
								<li><a href="<?php echo esc_url( $d[1] ); ?>"><?php echo esc_html( $d[0] ); ?></a></li>
								<?php endforeach; ?>
							</ul>
						</div>
						<?php if ( $c['card'] ) : ?>
						<a class="pi-mm__card" href="<?php echo esc_url( $c['card']['url'] ); ?>">
							<?php if ( $c['card']['img'] ) : ?><img src="<?php echo esc_url( $c['card']['img'] ); ?>" alt="<?php echo esc_attr( $c['card']['name'] ); ?>" loading="lazy" width="300" height="300"><?php endif; ?>
							<span class="pi-mm__card-body">
								<span class="pi-mm__card-tag">🏆 Il più venduto</span>
								<span class="pi-mm__card-name"><?php echo esc_html( $c['card']['name'] ); ?></span>
								<span class="pi-mm__card-price"><?php echo wp_kses_post( $c['card']['price'] ); ?></span>
							</span>
						</a>
						<?php endif; ?>
					</div>
					<footer class="pi-mm__strip">
						<span>🚚 Spedizione gratuita sopra 49 €</span><span>↩️ Reso entro 14 giorni</span><span>🛡️ Garanzia Italia 24 mesi</span>
					</footer>
				</section>
				<?php endforeach; ?>
			</div>
		</div>
	</div>
	<div class="pi-mm__layer" aria-hidden="true"></div>
</div>
		<?php
		return ob_get_clean();
	}
);

/**
 * Behaviour: hover-intent on desktop, click/tap toggle everywhere, Esc to close,
 * drill-down on mobile, focus handling for keyboard users.
 */
add_action(
	'wp_footer',
	function () {
		?>
<script>
(function () {
	var mq = window.matchMedia('(max-width: 1024px)');
	document.querySelectorAll('[data-pi-mm]').forEach(function (mm) {
		var btn = mm.querySelector('.pi-mm__trigger'), panel = mm.querySelector('.pi-mm__panel'),
			layer = mm.querySelector('.pi-mm__layer'), timer;
		function setPane(slug) {
			mm.querySelectorAll('.pi-mm__cat').forEach(function (a) { a.classList.toggle('is-active', a.dataset.pane === slug); });
			mm.querySelectorAll('.pi-mm__pane').forEach(function (p) { p.classList.toggle('is-active', p.dataset.pane === slug); });
		}
		function open() { clearTimeout(timer); if (!mq.matches) { layer.style.setProperty('--pi-mm-top', Math.max(0, panel.offsetParent ? panel.offsetParent.getBoundingClientRect().bottom : 0) + 'px'); } else { layer.style.setProperty('--pi-mm-top', '0px'); } mm.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); if (mq.matches) document.documentElement.classList.add('pi-mm-lock'); }
		function close() { clearTimeout(timer); mm.classList.remove('is-open', 'is-drill'); btn.setAttribute('aria-expanded', 'false'); document.documentElement.classList.remove('pi-mm-lock'); }
		btn.addEventListener('click', function () { mm.classList.contains('is-open') ? close() : open(); });
		mm.querySelector('.pi-mm__close').addEventListener('click', function () { close(); btn.focus(); });
		mm.querySelector('.pi-mm__back').addEventListener('click', function () { mm.classList.remove('is-drill'); });
		layer.addEventListener('click', close);
		window.addEventListener('scroll', function () { if (!mq.matches && mm.classList.contains('is-open')) close(); }, { passive: true });
		document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && mm.classList.contains('is-open')) { close(); btn.focus(); } });
		// Desktop: hover intent.
		mm.addEventListener('mouseenter', function () { if (!mq.matches) { clearTimeout(timer); timer = setTimeout(open, 120); } });
		mm.addEventListener('mouseleave', function () { if (!mq.matches) { clearTimeout(timer); timer = setTimeout(close, 220); } });
		mm.querySelectorAll('.pi-mm__cat').forEach(function (a) {
			a.addEventListener('mouseenter', function () { if (!mq.matches) setPane(a.dataset.pane); });
			a.addEventListener('focus', function () { if (!mq.matches) setPane(a.dataset.pane); });
			a.addEventListener('click', function (e) {
				if (mq.matches) { e.preventDefault(); setPane(a.dataset.pane); mm.classList.add('is-drill'); mm.querySelector('.pi-mm__title').textContent = a.dataset.title; }
			});
		});
		mm.querySelector('.pi-mm__back').addEventListener('click', function () { mm.querySelector('.pi-mm__title').textContent = '🛍️ Tutte le categorie'; });
	});
})();
</script>
		<?php
	},
	98
);
