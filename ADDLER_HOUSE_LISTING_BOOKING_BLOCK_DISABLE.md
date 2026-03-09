# Addler House – Disattivare il blocco di prenotazione (vecchio sistema)

Tutto è gestito **solo tramite snippet** in Code Snippets (nessun intervento su child theme o Editor del tema).

---

## Snippet in uso (listing e homepage)

| Snippet | File | Cosa fa |
|--------|------|--------|
| **Listing – Rimuovi Book Now e mostra Custom Widget 1 e 2** | `snippet-listing-remove-book-now-add-custom-widgets.php` | Rimuove il link WuBook "Book Now", la barra "/night", inietta nella sidebar destra il contenuto di Custom Sidebar 1 e 2 (widget "Book your accommodation in Venice" / "in Sicily" – CiaoBooking). |
| **Listing – Nascondi il blocco di prenotazione (vecchio sistema)** | `snippet-listing-hide-booking-block.php` | Nasconde solo l’overlay/modulo del tema con "Request to Book". **Non** nasconde il contenuto di `#listing-custom-widgets-inject` (i due widget Venice/Sicily). In homepage nasconde il box "Addler House - Book now your next stay!" con pulsante Search. |

Altri snippet Addler House (homepage widget sopra slider, menu/logo mobile): v. `snippet-homey-homepage-widget-above-slider.php` e documento generato da `create_addler_house_snippets_doc.py`.

---

## Comportamento dello snippet "Nascondi blocco di prenotazione"

### Su pagine listing (single listing)

- **CSS**: nasconde solo l’**overlay/modulo** del tema Homey (il blocco con "Request to Book"):
  - `#overlay-booking-module`, `.overlay-booking-module`
  - `.sidebar-booking-module`, `.sidebar-booking-module-body`
- **Nessuna** regola CSS sulla sidebar che possa colpire i widget dentro `#listing-custom-widgets-inject` (in passato selettori tipo `[class*="booking-widget"]` nascondevano anche i widget CiaoBooking perché contengono "booking" nel nome classe; sono stati rimossi).
- **JS**: `hideThemeBookingOverlay()` nasconde solo gli elementi con quelle classi/id e **non** tocca elementi che contengono o sono contenuti in `#listing-custom-widgets-inject`. La funzione `findAndHideBlock()` salta tutto il contenuto dentro `#listing-custom-widgets-inject` e usa solo marker testuali specifici del tema ("Request to book", "Richiedi prenotazione", ecc.), non "Adults"/"Children"/"Apply" per evitare di nascondere i form CiaoBooking.

Risultato: il vecchio blocco "Request to Book" è nascosto; i due widget "Book your accommodation in Venice" e "in Sicily" restano visibili nella sidebar.

### In homepage

- **CSS**: nasconde il box bianco "Addler House - Book now your next stay!" con pulsante Search (`.banner-caption-side-search`, `.side-search-wrap`, ecc.).

---

## Perché il modulo "Request to Book" non stava nella sidebar

Sul sito il blocco con il pulsante **"Request to Book"** è in un **overlay** del tema Homey, non dentro `.sidebar.right-sidebar`:

- Contenitore: `#overlay-booking-module` (classe `overlay-booking-module`)
- Contenuto: `.sidebar-booking-module` → `.sidebar-booking-module-body` → pulsante "Request to Book"

Nella sidebar destra viene invece iniettato solo il contenuto di Custom Widget 1 e 2 (contenitore `#listing-custom-widgets-inject`). Lo snippet "Nascondi blocco di prenotazione" agisce quindi solo sull’overlay (e in homepage sul banner Search), senza toccare l’inject.

---

## Cosa fare per aggiornare

1. Apri **Code Snippets** in WordPress.
2. Modifica lo snippet **"Listing – Nascondi il blocco di prenotazione"** e incolla il codice aggiornato da `snippet-listing-hide-booking-block.php`.
3. Salva e verifica su una pagina listing (es. https://www.addlerhouse.com/listing/suite-superior-colombo/ ):
   - Il modulo con "Request to Book" non deve essere visibile.
   - I due widget "Book your accommodation in Venice" e "in Sicily" devono essere visibili nella sidebar.

---

## Modifiche (26 feb 2026)

- Rimosse tutte le regole CSS su `.sidebar.right-sidebar` (`.block-booking`, `[class*="booking-widget"]`, `[class*="detail-booking"]`, ecc.) che nascondevano anche i widget CiaoBooking dentro `#listing-custom-widgets-inject`.
- Mantenute solo le regole sull’overlay (`#overlay-booking-module`, `.sidebar-booking-module`, ecc.).
- Nel JS: esclusione esplicita di tutto il contenuto dentro `#listing-custom-widgets-inject` (con `node.closest('#' + skipId)`); rimossi dai marker testuali "Adults", "Children", "Apply"; il regex sui link cerca solo "request to book" / "richiedi prenotazione" (non "book now") per non nascondere i CTA dei widget Venice/Sicily.
