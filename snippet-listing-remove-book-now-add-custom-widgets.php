<?php
/**
 * Snippet Code Snippets: Listing - Rimuovi "Book Now" e mostra Custom Widget 1 e 2
 *
 * - Si attiva solo su pagine singola listing (single listing).
 * - Rimuove il pulsante/link "Book Now" (WuBook) dalla sidebar destra.
 * - Inserisce nella stessa sidebar il contenuto di Custom Sidebar 1 e Custom Sidebar 2.
 * - Su smartphone: i widget hanno z-index basso così il menu hamburger resta sopra; ogni altro "Book Now" (WuBook) e la barra con "/night" in basso vengono nascosti e rimossi.
 *
 * Uso: incolla in Code Snippets come snippet PHP (esecuzione "Run everywhere").
 * Se il tema usa un post type diverso da 'listing', cambia is_singular('listing').
 * Se le aree widget si chiamano diversamente (es. homey_custom_1), sostituisci
 * 'custom-sidebar-1' e 'custom-sidebar-2' con gli ID corretti.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// 1) Nascondere subito il pulsante Book Now (evita flash) — solo su single listing
add_action( 'wp_head', 'listing_hide_book_now_button_css', 5 );
function listing_hide_book_now_button_css() {
	if ( ! is_singular( 'listing' ) ) {
		return;
	}
	?>
	<style id="listing-hide-book-now">
		.sidebar.right-sidebar a[href*="wubook"] { display: none !important; }
		/* Smartphone: nascondi Book Now, barra prezzo/night e widget sotto il menu */
		@media (max-width: 991px) {
			a[href*="wubook"],
			.sticky-footer a[href*="wubook"],
			[class*="sticky"] a[href*="wubook"],
			[class*="fixed-bottom"] a[href*="wubook"],
			.btn-primary[href*="wubook"],
			button a[href*="wubook"] { display: none !important; }
			.listing-detail-footer, [class*="listing-footer"], [class*="sticky-footer"],
			[class*="price-bar"], [class*="fixed-bottom"][class*="listing"] { display: none !important; }
			#listing-custom-widgets-inject,
			.sidebar.right-sidebar .listing-custom-widget-area {
				position: relative;
				z-index: 0;
			}
		}
	</style>
	<?php
}

// 2) Su single listing: output dei due custom widget nella pagina (per poi spostarli in sidebar via JS)
add_action( 'wp_footer', 'listing_output_custom_widgets_for_sidebar', 5 );
function listing_output_custom_widgets_for_sidebar() {
	if ( ! is_singular( 'listing' ) ) {
		return;
	}
	if ( ! is_active_sidebar( 'custom-sidebar-1' ) && ! is_active_sidebar( 'custom-sidebar-2' ) ) {
		return;
	}
	?>
	<div id="listing-custom-widgets-inject" style="display:none;" aria-hidden="true">
		<?php
		if ( is_active_sidebar( 'custom-sidebar-1' ) ) {
			echo '<div class="listing-custom-widget-area listing-custom-widget-1">';
			dynamic_sidebar( 'custom-sidebar-1' );
			echo '</div>';
		}
		if ( is_active_sidebar( 'custom-sidebar-2' ) ) {
			echo '<div class="listing-custom-widget-area listing-custom-widget-2">';
			dynamic_sidebar( 'custom-sidebar-2' );
			echo '</div>';
		}
		?>
	</div>
	<?php
}

// 3) JS: rimuovere il nodo del Book Now e iniettare i due widget nella sidebar destra
add_action( 'wp_footer', 'listing_inject_custom_widgets_script', 20 );
function listing_inject_custom_widgets_script() {
	if ( ! is_singular( 'listing' ) ) {
		return;
	}
	?>
	<script>
	(function() {
		var wrap = document.getElementById('listing-custom-widgets-inject');
		var sidebar = document.querySelector('.sidebar.right-sidebar');

		// Rimuovi tutti i link "Book Now" (WuBook) in tutta la pagina
		document.querySelectorAll('a[href*="wubook"]').forEach(function(el) {
			var parent = el.parentNode;
			el.remove();
			if (parent && (parent.tagName === 'BUTTON' || parent.classList.contains('book-now') || (parent.childNodes.length === 0))) {
				parent.remove();
			}
		});

		// Rimuovi la barra in basso che contiene "/night" (prezzo per notte)
		(function removeNightBar() {
			var walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
			var node, el;
			while (node = walk.nextNode()) {
				if (node.textContent && node.textContent.indexOf('/night') !== -1) {
					el = node.parentElement;
					while (el && el !== document.body) {
						var style = window.getComputedStyle(el);
						var pos = style.position;
						var cls = el.className || '';
						if (pos === 'fixed' || pos === 'sticky' || /sticky|fixed|bottom|footer|price|listing-detail/.test(cls)) {
							el.remove();
							return;
						}
						el = el.parentElement;
					}
				}
			}
		})();

		if (wrap && sidebar) {
			wrap.style.display = '';
			wrap.removeAttribute('aria-hidden');
			sidebar.insertBefore(wrap, sidebar.firstChild);
		}
	})();
	</script>
	<?php
}
