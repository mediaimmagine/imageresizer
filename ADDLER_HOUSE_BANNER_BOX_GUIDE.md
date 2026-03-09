# Addler House – Guida al box hero (sandbox-ah.mediaimmagine.it)

## Dove si trova il box

Il box bianco con titolo **"ADDLER HOUSE"**, sottotitolo **"Book now your next stay!"** e pulsante **"Search"** è il **banner di ricerca** in homepage.

### Struttura HTML e classi CSS

| Elemento | Selettore / Classe | Contenuto attuale |
|----------|--------------------|-------------------|
| **Contenitore esterno** | `div.banner-caption.banner-caption-side-search` | Wrapper della caption sopra lo slider |
| **Box bianco** | `div.side-search-wrap` | Box con sfondo bianco, bordi arrotondati (6px), ombra |
| **Titolo** | `h2.banner-title` | "Addler House" |
| **Sottotitolo** | `p.banner-subtitle` | "Book now your next stay!" |
| **Form di ricerca** | `.search-wrap.search-banner.search-banner-desktop` | Form che invia a `/search-results/` |
| **Pulsante** | `button.btn.btn-primary` | "Search" (submit del form) |

Il box è generato dal **tema Homey** nella homepage, dentro la sezione banner/slider.

### Dove si attiva/disattiva e si modifica il box

- **Pagina**: **Home** (la pagina usata come homepage).
- **Sezione in editor**: **Page Header Options** (opzioni intestazione pagina).
- Da lì si possono **attivare/disattivare** il box e modificare **titolo** (Header title) e **sottotitolo** (Header subtitle). I valori sono salvati come custom field della pagina (`header_title`, `header_subtitle`) e stampati dal template `template-parts/banner/caption.php`.

---

## Come configurarlo o modificarlo

### 1. Testo (titolo e sottotitolo) e visibilità del box

- **Pagine → Home → Modifica** (o Modifica con Elementor).
- Nel pannello della pagina cercare **Page Header Options**.
- Modificare **Header title** e **Header subtitle**, oppure **disattivare** il page header per nascondere il box.

### 2. Stile del box (CSS)

Per modificare aspetto e posizione senza toccare il tema, usa un **child theme** o **CSS aggiuntivo** (Personalizza → CSS aggiuntivo / plugin di CSS).

Classi utili:

```css
/* Box bianco (contenitore principale) */
.side-search-wrap {
  background-color: #fff;      /* già bianco */
  border-radius: 6px;          /* angoli arrotondati */
  box-shadow: ...;             /* ombra */
  padding: 20px;               /* regola spazio interno */
}

/* Titolo "ADDLER HOUSE" */
.banner-caption-side-search .banner-title {
  font-size: 2rem;
  color: #333;
  text-transform: uppercase;
}

/* Sottotitolo "Book now your next stay!" */
.banner-caption-side-search .banner-subtitle {
  font-size: 1rem;
  color: #666;
}

/* Pulsante "Search" (marrone/beige) */
.banner-caption-side-search .btn-primary {
  background-color: #c4a574;   /* colore attuale tipo marrone */
  color: #fff;
  border-radius: 4px;
}
```

Modificando questi selettori puoi cambiare colori, font, dimensioni e padding del box.

### 3. Comportamento del pulsante "Search"

Il pulsante è un **submit** di un form:

- **Action del form**: `https://www.sandbox-ah.mediaimmagine.it/search-results/` (metodo GET).
- Per cambiare dove porta la ricerca: modificare l'`action` del form nel template che genera `.side-search-wrap` (stesso file dove sono titolo/sottotitolo).
- Per cambiare solo l'etichetta "Search": cercare nel tema la stringa "Search" (o la traduzione in .po/.pot) e sostituirla, oppure usare un plugin di traduzione (es. Loco Translate, WPML) per quella stringa.

### 4. File template (riferimento)

- **Template che stampa titolo/sottotitolo**: tema Homey → `template-parts/banner/caption.php` (legge i custom field `header_title` e `header_subtitle` della pagina).

---

## Riepilogo

| Cosa modificare | Dove intervenire |
|----------------|------------------|
| Attivare/disattivare il box | **Home** → **Page Header Options** (disattivare page header) |
| Titolo "Addler House" | **Home** → **Page Header Options** → Header title |
| Sottotitolo "Book now your next stay!" | **Home** → **Page Header Options** → Header subtitle |
| Testo pulsante "Search" | Template o file di traduzione |
| Colori, font, dimensioni del box | CSS aggiuntivo o child theme (`.side-search-wrap`, `.banner-title`, `.banner-subtitle`, `.btn-primary`) |
| Destinazione ricerca | Template: attributo `action` del form dentro `.side-search-wrap` |

Il box è **solo sulla homepage** nella sezione banner; non è presente nel repository **imageresizer** perché il sito live è gestito dal tema WordPress sul server.

---

## Verifica in wp-admin (26 feb 2026)

### Dove si controlla il box (definitivo)

- **Pagina**: **Home**.
- **Sezione**: **Page Header Options** (opzioni intestazione pagina).
- Da lì si attiva/disattiva il box e si modificano titolo e sottotitolo (Header title, Header subtitle). Template tema: `template-parts/banner/caption.php`.

### Contesto tecnico

- **Tema**: Homey (Favethemes) + child **Homey Child**.
- **Sezione HTML**: `section.top-banner-wrap.top-banner-sr` → il box è `.banner-caption-side-search` > `.side-search-wrap`.
- **Slider**: **Slider Revolution** – modulo **"Homepage Slider"** (sfondo/immagini del banner).
- **Homey Options**: i tab controllati (General, Labels, Search, Header Nav, Listings) non contengono campi per titolo/sottotitolo del box; questi sono gestiti a livello di **pagina** (Page Header Options).
