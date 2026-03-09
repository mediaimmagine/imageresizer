<?php
/**
 * Snippet Code Snippets: Nascondi i blocchi del vecchio sistema di prenotazione
 *
 * Nasconde SOLO:
 * 1) Su listing: overlay/modulo tema con "Request to Book" (non tocca "Book your accommodation in Venice/Sicily").
 * 2) In homepage: il box "Addler House - Book now your next stay!" con pulsante Search (vecchio banner).
 *
 * NON nasconde: i widget "Book your accommodation in Venice" / "in Sicily" (Custom Widget 1 e 2 / CiaoBooking).
 *
 * Uso: Code Snippets, snippet PHP, esecuzione "Run everywhere".
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/* Homepage: nascondi solo il box "Addler House - Book now your next stay!" (Search). Non tocca Venice/Sicily. */
add_action( 'wp_head', 'addler_hide_old_banner_book_now_css', 5 );
function addler_hide_old_banner_book_now_css() {
	if ( ! is_front_page() ) {
		return;
	}
	?>
	<style id="addler-hide-old-banner-book-now">
		.banner-caption-side-search,
		.side-search-wrap,
		.search-banner-desktop.side-search-wrap,
		.banner-caption.banner-caption-side-search { display: none !important; visibility: hidden !important; height: 0 !important; overflow: hidden !important; }
	</style>
	<?php
}

add_action( 'wp_head', 'listing_hide_booking_block_css', 6 );
function listing_hide_booking_block_css() {
	if ( ! is_singular( 'listing' ) ) {
		return;
	}
	?>
	<style id="listing-hide-booking-block">
		/* Solo overlay/modulo tema (Request to Book). NON toccare #listing-custom-widgets-inject (Venice/Sicily). */
		body.single-listing #overlay-booking-module,
		body.single-listing .overlay-booking-module,
		body.single-listing .sidebar-booking-module,
		body.single-listing .sidebar-booking-module-body,
		body.listing-template-default #overlay-booking-module,
		body.listing-template-default .overlay-booking-module,
		#overlay-booking-module,
		.overlay-booking-module,
		.sidebar-booking-module,
		.sidebar-booking-module-body { display: none !important; visibility: hidden !important; height: 0 !important; overflow: hidden !important; opacity: 0 !important; pointer-events: none !important; }
	</style>
	<?php
}

add_action( 'wp_footer', 'listing_hide_booking_block_js', 21 );
function listing_hide_booking_block_js() {
	if ( ! is_singular( 'listing' ) ) {
		return;
	}
	?>
	<script>
	(function() {
		var skipId = 'listing-custom-widgets-inject';
		var skipClass = 'listing-custom-widget-area';

		function hideThemeBookingOverlay() {
			var sel = '#overlay-booking-module, .overlay-booking-module, .sidebar-booking-module, .sidebar-booking-module-body, .homey_notification.search-wrap.search-banner';
			document.querySelectorAll(sel).forEach(function(el) {
				if (el.id === skipId || (el.querySelector && el.querySelector('#' + skipId))) return;
				el.style.setProperty('display', 'none', 'important');
				el.style.setProperty('visibility', 'hidden', 'important');
				el.style.setProperty('height', '0', 'important');
				el.style.setProperty('overflow', 'hidden', 'important');
				el.style.setProperty('opacity', '0', 'important');
				el.style.setProperty('pointer-events', 'none', 'important');
			});
		}

		function run() {
			hideThemeBookingOverlay();
			var sidebar = document.querySelector('.sidebar.right-sidebar');
			var sticky = document.querySelector('.sidebar.right-sidebar .theiaStickySidebar');
			var container = sticky || sidebar;
			if (!container) return false;

			function findAndHideBlock() {
				var inject = document.getElementById(skipId);
				var markers = ['Request to book', 'Request to Book', 'You won\'t be charged', '/night', 'Prenota', 'Richiedi prenotazione'];
				var walker = document.createTreeWalker(container, NodeFilter.SHOW_ELEMENT, null, false);
				var node;
				while (node = walker.nextNode()) {
					if (inject && (node === inject || node.id === skipId)) continue;
					if (inject && node.closest && node.closest('#' + skipId)) continue;
					var c = typeof node.className === 'string' ? node.className : '';
					if (c.indexOf(skipClass) >= 0) continue;
					var text = node.textContent || '';
					for (var m = 0; m < markers.length; m++) {
						if (text.indexOf(markers[m]) === -1) continue;
						var el = node;
						while (el && el !== document.body) {
							if (!container.contains(el)) break;
							var parent = el.parentElement;
							if (!parent || parent === container) {
								el.style.setProperty('display', 'none', 'important');
								return true;
							}
							el = parent;
						}
						break;
					}
				}
				return false;
			}

			if (findAndHideBlock()) return true;
			var links = container.querySelectorAll('a, button');
			var inject = document.getElementById(skipId);
			for (var i = 0; i < links.length; i++) {
				if (inject && (links[i] === inject || links[i].closest('#' + skipId))) continue;
				var t = (links[i].textContent || '').trim();
				if (!/request to book|richiedi prenotazione/i.test(t)) continue;
				var el = links[i].parentElement;
				while (el && el !== document.body && container.contains(el)) {
					var p = el.parentElement;
					if (!p || p === container) {
						el.style.setProperty('display', 'none', 'important');
						return true;
					}
					el = p;
				}
				break;
			}
			return false;
		}

		if (document.readyState === 'loading') {
			document.addEventListener('DOMContentLoaded', function() {
				run();
				setTimeout(run, 500);
				setTimeout(hideThemeBookingOverlay, 800);
			});
		} else {
			run();
			setTimeout(run, 500);
			setTimeout(hideThemeBookingOverlay, 800);
		}
	})();
	</script>
	<?php
}
