#!/usr/bin/env python3
"""Crea il documento Word con i due snippet Code Snippets e la guida per Addler House."""

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("Installare python-docx: pip install python-docx")
    raise

def set_cell_shading(cell, color):
    """Imposta sfondo di una cella (es. #f5f5f5)."""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)

def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.bold = True
    if level == 1:
        run.font.size = Pt(16)
    else:
        run.font.size = Pt(13)
    return p

def add_code_paragraph(doc, code, font_name='Consolas', font_size=9):
    """Aggiunge un paragrafo con codice in monospace."""
    for line in code.split('\n'):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line if line.strip() else ' ')
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.italic = False
        run.font.bold = False
    return doc

def main():
    doc = Document()
    doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run('Snippet Code Snippets per Addler House')
    r.bold = True
    r.font.size = Pt(18)
    doc.add_paragraph()
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run('Sito: sandbox-ah.mediaimmagine.it — Tema Homey (Favethemes)').font.size = Pt(11)
    doc.add_paragraph()

    # Intro
    add_heading(doc, 'Introduzione', 1)
    doc.add_paragraph(
        'Questo documento descrive i tre snippet PHP realizzati per il sito Addler House (addlerhouse.com / sandbox-ah.mediaimmagine.it), '
        'da inserire tramite il plugin Code Snippets di WordPress. Gli snippet modificano il comportamento del tema '
        'Homey senza alterare i file del tema: tutto avviene via plugin, in modo reversibile e aggiornabile.'
    )
    doc.add_paragraph(
        'Requisito: plugin Code Snippets installato e attivo. Ogni snippet va creato come "PHP Snippet" con '
        'esecuzione "Run everywhere", poi incollato nel corpo dello snippet (il tag <?php iniziale è incluso).'
    )

    # --- SNIPPET 1 ---
    add_heading(doc, 'Snippet 1: Homepage – Widget sopra slider, menu e logo (smartphone)', 1)
    add_heading(doc, 'Applicazione al sito Addler House', 2)
    doc.add_paragraph(
        'Lo snippet agisce sulla homepage e, su smartphone, su tutte le pagine per header e logo.'
    )
    doc.add_paragraph('Cosa fa:', style='List Bullet')
    doc.add_paragraph(
        'In homepage: mostra un box trasparente sopra lo slider con i widget delle aree "Homepage sopra slider - Area 1/2", '
        'oppure Custom Sidebar 1 e Custom Sidebar 2 se configurati. Su desktop il box è centrato con gap 20px; '
        'su smartphone (≤767px) il box è leggermente più in alto, con un widget per volta e swipe orizzontale (scroll-snap).',
        style='List Bullet'
    )
    doc.add_paragraph(
        'Su tutte le pagine, solo su smartphone: il menu hamburger resta sopra al box widget (z-index più alto), '
        'così le voci del menu restano cliccabili; il logo in header viene ingrandito (scale 1.55, altezza 52px), '
        'centrato e con spazio bianco sopra e sotto (padding 12px).',
        style='List Bullet'
    )
    doc.add_paragraph(
        'Dove si vede: homepage (box sopra lo slider); qualsiasi pagina da smartphone (logo più grande e menu utilizzabile).'
    )
    add_heading(doc, 'Codice Snippet 1 (PHP)', 2)
    with open('snippet-homey-homepage-widget-above-slider.php', 'r', encoding='utf-8') as f:
        snippet1 = f.read()
    add_code_paragraph(doc, snippet1)

    # --- SNIPPET 2 ---
    add_heading(doc, 'Snippet 2: Listing – Rimuovi Book Now (WuBook) e mostra Custom Widget 1 e 2', 1)
    add_heading(doc, 'Applicazione al sito Addler House', 2)
    doc.add_paragraph(
        'Lo snippet agisce solo sulle pagine singole di listing (es. Suite Superior Colombo e le altre sistemazioni).'
    )
    doc.add_paragraph('Cosa fa:', style='List Bullet')
    doc.add_paragraph(
        'Rimuove dalla sidebar destra il pulsante/link "Book Now" che punta al vecchio sistema di prenotazione WuBook.',
        style='List Bullet'
    )
    doc.add_paragraph(
        'Nella stessa area della sidebar inserisce il contenuto di Custom Widget 1 e Custom Widget 2 (aree widget '
        'custom-sidebar-1 e custom-sidebar-2), così si possono mostrare CTA o informazioni di prenotazione alternative.',
        style='List Bullet'
    )
    doc.add_paragraph(
        'Su smartphone: nasconde e rimuove anche eventuali altri pulsanti "Book Now" (es. in una barra fissa in basso) '
        'e la barra bianca con la dicitura "/night" (prezzo per notte), evitando che resti visibile il vecchio sistema.',
        style='List Bullet'
    )
    doc.add_paragraph(
        'I widget iniettati hanno z-index basso su mobile così il menu hamburger resta sopra e utilizzabile.',
        style='List Bullet'
    )
    doc.add_paragraph(
        'Dove si vede: pagine singole listing, es. https://www.sandbox-ah.mediaimmagine.it/listing/suite-superior-colombo/ — '
        'sidebar destra con Custom Widget 1 e 2 al posto di Book Now; su smartphone nessun Book Now e nessuna barra "/night" in basso.'
    )
    add_heading(doc, 'Codice Snippet 2 (PHP)', 2)
    with open('snippet-listing-remove-book-now-add-custom-widgets.php', 'r', encoding='utf-8') as f:
        snippet2 = f.read()
    add_code_paragraph(doc, snippet2)

    # --- SNIPPET 3 ---
    add_heading(doc, 'Snippet 3: Listing – Nascondi il blocco di prenotazione (vecchio sistema)', 1)
    add_heading(doc, 'Applicazione al sito Addler House', 2)
    doc.add_paragraph(
        'Lo snippet agisce sulle pagine singole di listing e in homepage. Non tocca i widget "Book your accommodation in Venice/Sicily" (CiaoBooking).'
    )
    doc.add_paragraph('Cosa fa:', style='List Bullet')
    doc.add_paragraph(
        'Su listing: nasconde solo l\'overlay/modulo del tema con "Request to Book" (CSS su #overlay-booking-module, .sidebar-booking-module; '
        'JS che non nasconde mai il contenuto di #listing-custom-widgets-inject).',
        style='List Bullet'
    )
    doc.add_paragraph(
        'In homepage: nasconde il box "Addler House - Book now your next stay!" con pulsante Search (vecchio banner).',
        style='List Bullet'
    )
    doc.add_paragraph(
        'Dove si vede: pagine listing senza modulo "Request to Book" e con i due widget Venice/Sicily visibili; homepage senza il box Search sopra lo slider.'
    )
    add_heading(doc, 'Codice Snippet 3 (PHP)', 2)
    with open('snippet-listing-hide-booking-block.php', 'r', encoding='utf-8') as f:
        snippet3 = f.read()
    add_code_paragraph(doc, snippet3)

    # Note finali
    add_heading(doc, 'Note operative', 1)
    doc.add_paragraph(
        'Tutti e tre gli snippet vanno incollati in Code Snippets come nuovo snippet PHP, con esecuzione "Run everywhere". '
        'Se il tema usa un post type diverso da "listing" per le sistemazioni, negli Snippet 2 e 3 sostituire is_singular(\'listing\') '
        'con il post type corretto. Se le aree widget hanno ID diversi (es. homey_custom_1), aggiornare gli ID negli snippet. '
        'Riferimento: ADDLER_HOUSE_LISTING_BOOKING_BLOCK_DISABLE.md.'
    )
    doc.add_paragraph()
    doc.add_paragraph('Documento generato il 26 febbraio 2026 — COED IA mediaimmagine.').alignment = WD_ALIGN_PARAGRAPH.CENTER

    out = 'Addler_House_Snippet_Code_Snippets.docx'
    doc.save(out)
    print(f'Creato: {out}')

if __name__ == '__main__':
    main()
