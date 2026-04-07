Preventivatore siti WordPress + Elementor — uso su macOS (portable)
================================================================

Contenuto
---------
- preventivo_siti.py   : applicazione con interfaccia grafica (tkinter)
- prezzi_nordest.json  : listino prezzi e opzioni (modificabile)

Requisiti
---------
- Python 3.9 o successivo (consigliato da https://www.python.org/downloads/macos/ )
- tkinter: incluso nell’installer ufficiale Python.org.
  Se usi Homebrew e manca la GUI:
    brew install python-tk
  oppure installa Python dal sito python.org.

Avvio
-----
Da Terminale, nella cartella che contiene questi file:

  cd /percorso/preventivo_siti_wordpress
  python3 preventivo_siti.py

Su macOS, per impostazione predefinita si apre il browser su http://127.0.0.1:…
(interfaccia web locale, niente dipendenze extra). Il terminale mostra l’URL e
resta in attesa: premi Invio per chiudere il server.

Per forzare la vecchia finestra Tk invece del browser:

  PREVENTIVATORE_TK=1 python3 preventivo_siti.py

Oppure, dopo aver reso eseguibile lo script (opzionale):

  chmod +x preventivo_siti.py
  ./preventivo_siti.py

Dipendenze
----------
Nessun pacchetto pip: solo libreria standard Python.

Sviluppo
--------
- Aggiorna i prezzi in prezzi_nordest.json (UTF-8).
- CONFIG_PATH in preventivo_siti.py punta al JSON nella stessa cartella dello script.
