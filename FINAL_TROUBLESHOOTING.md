# Troubleshooting Finale - Upload WordPress

## Situazione Attuale

- ✅ REST API non bloccato (GET funziona)
- ✅ Application Password funziona (GET funziona)
- ✅ Utente ha ruolo Editor
- ❌ POST requests falliscono con 401 "rest_cannot_create"
- ❌ Non può accedere a contesto "edit" nel REST API

## Test Manuale da Fare

### Test 1: Upload Manuale da WordPress Dashboard

1. **Login** a WordPress con utente "COED Image Resizer"
2. **Vai a:** Media → Aggiungi nuovo
3. **Prova** a caricare un'immagine
4. **Risultato?**
   - ✅ Se funziona: Il problema è nella configurazione REST API
   - ❌ Se non funziona: Il problema è nei permessi utente WordPress

### Test 2: Verifica Capabilities Utente

1. **Installa plugin:** "User Role Editor" (temporaneamente)
2. **Vai a:** Users → User Role Editor
3. **Seleziona:** "COED Image Resizer"
4. **Verifica** che abbia queste capabilities:
   - ✅ `upload_files`
   - ✅ `edit_posts`
   - ✅ `create_posts`

## Possibili Soluzioni

### Soluzione 1: Verifica Plugin che Limitano Permessi

Plugin comuni che limitano capabilities:
- **Members** - Verifica impostazioni ruoli
- **Advanced Access Manager** - Controlla restrizioni
- **User Role Editor** - Verifica capabilities
- **WP Cerber** - Potrebbe avere restrizioni su capabilities

### Soluzione 2: Aggiungi Capability Manualmente

Se hai accesso a User Role Editor:

1. **Vai a:** Users → User Role Editor
2. **Seleziona:** "COED Image Resizer" 
3. **Aggiungi** queste capabilities:
   - `upload_files` ✓
   - `edit_posts` ✓
   - `create_posts` ✓
4. **Salva**

### Soluzione 3: Usa Ruolo Amministratore Temporaneamente

Per testare se è un problema di permessi:

1. **Cambia ruolo** a "Amministratore" temporaneamente
2. **Esegui test:** `python3 test_wp_upload_direct.py`
3. **Se funziona:** Il problema è nei permessi Editor
4. **Se non funziona:** Il problema è altrove

### Soluzione 4: Verifica WP Cerber per POST Requests

1. **Vai a:** Cerber → Activity → Log
2. **Cerca** richieste POST a `/wp-json/wp/v2/media`
3. **Verifica** se sono bloccate
4. **Se bloccate:** Aggiungi alla whitelist

### Soluzione 5: Controlla Altri Plugin di Sicurezza

Plugin che potrebbero bloccare POST:
- **Wordfence** - Firewall potrebbe bloccare POST
- **iThemes Security** - Restrizioni REST API
- **All In One WP Security** - Blocchi POST

## Prossimi Passi

1. **Esegui test manuale** (upload da dashboard)
2. **Riporta risultato** - questo ci dirà se è problema permessi o configurazione
3. **In base al risultato** procediamo con la soluzione appropriata

