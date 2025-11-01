# Rigenera Application Password

## Problema Rilevato

Il test mostra che:
- ✅ GET requests funzionano (può leggere media library)
- ❌ POST requests falliscono (non può uploadare)

Questo indica che l'Application Password potrebbe non essere configurato correttamente per le operazioni POST.

## Soluzione: Rigenera Application Password

### Step 1: Elimina il Vecchio Application Password

1. **Vai a:** WordPress Dashboard → Utenti → Profilo (per l'utente "COED Image Resizer")
   - Oppure: Utenti → Modifica "COED Image Resizer" → Profilo
2. **Scorri in basso** fino a "Application Passwords"
3. **Trova** l'Application Password esistente
4. **Clicca** "Revoke" o "Revoca" per eliminarlo

### Step 2: Crea un Nuovo Application Password

1. **Nella sezione "Application Passwords"**
2. **Inserisci un nome:** `Image Resizer App` (o qualsiasi nome descrittivo)
3. **Clicca:** "Add New Application Password" o "Aggiungi nuova password applicazione"
4. **COPIA IMMEDIATAMENTE** la password generata (la vedrai solo una volta!)
   - Formato: `XXXX XXXX XXXX XXXX XXXX XXXX` (con spazi)

### Step 3: Aggiorna il Test Script

Apri `test_wp_upload_direct.py` e sostituisci:
```python
WP_APP_PASSWORD = "Hz1U RYxx PaVE 6x4O hKce yhgC"
```
con la nuova password.

### Step 4: Test di Nuovo

Dopo aver rigenerato:
```bash
python3 test_wp_upload_direct.py
```

## Note Importanti

- L'Application Password deve essere copiato ESATTAMENTE come mostrato
- Include gli spazi tra i gruppi di caratteri
- Non rimuovere gli spazi
- Copialo subito perché WordPress lo mostra solo una volta

## Verifica Utente

Prima di rigenerare, verifica che:
- ✅ L'utente "COED Image Resizer" esista
- ✅ Ha ruolo **Editor**
- ✅ L'email utente è corretta
- ✅ L'utente è attivo (non cancellato/spam)

## Alternativa: Verifica Impostazioni Application Password

Se preferisci non rigenerare, verifica:
1. L'Application Password è ancora attivo (non revocato)
2. Non ci sono plugin che limitano Application Passwords
3. L'utente non ha limitazioni speciali impostate

## Dopo la Rigenerazione

Quando avrai la nuova password, possiamo:
1. Testare immediatamente
2. Configurarla nell'app Image Resizer
3. Verificare che gli upload funzionino

