# Fix Permessi Utente WordPress

## Situazione Attuale

✅ **REST API non è più bloccato!** (prima era 403, ora è 401)
✅ **Autenticazione funziona!** (WordPress riconosce l'utente)
❌ **Permessi insufficienti** per upload media

## Errore Ricevuto

```
401 - "Non hai i permessi per creare articoli con questo utente"
```

Questo significa che l'utente "COED Image Resizer" non ha la capacità `upload_files`.

## Soluzione: Modifica Ruolo Utente

### Step 1: Vai alle Impostazioni Utente

1. **Vai a:** Dashboard WordPress → Utenti → Tutti gli utenti
2. **Trova:** "COED Image Resizer"
3. **Clicca:** "Modifica" o passa sopra e clicca "Modifica"

### Step 2: Cambia il Ruolo

1. **Trova la sezione:** "Ruolo"
2. **Seleziona uno di questi ruoli:**
   - ✅ **Editor** (consigliato - può gestire media ma non modificare impostazioni)
   - ✅ **Amministratore** (ha tutti i permessi)

### Step 3: Salva

1. **Clicca:** "Aggiorna utente" (in basso)
2. **Aspetta** conferma di salvataggio

### Step 4: Test di Nuovo

Dopo aver cambiato il ruolo, testa:
```bash
python3 test_wp_upload_direct.py
```

## Ruoli WordPress e Capacità

| Ruolo | Può Upload Media? | Note |
|-------|-------------------|------|
| Sottoscrittore | ❌ NO | Solo lettura |
| Collaboratore | ❌ NO | Può scrivere ma non pubblicare |
| Autore | ✅ SÌ | Può gestire i propri post e media |
| **Editor** | ✅ **SÌ** | **Consigliato - gestisce media di tutti** |
| **Amministratore** | ✅ **SÌ** | Ha tutti i permessi |

## Verifica Permessi

Se vuoi verificare le capacità dell'utente:

1. **Vai a:** Utenti → Modifica "COED Image Resizer"
2. **Scorri in basso** e cerca "Capacità" o "Capabilities"
3. **Verifica** che ci sia `upload_files` nella lista

## Se Il Ruolo È Già Editor/Amministratore

Se l'utente ha già ruolo Editor o Amministratore ma ancora dà errore:

1. **Verifica plugin** che potrebbero limitare capacità utente
2. **Controlla** se ci sono plugin di gestione ruoli installati
3. **Prova** a creare un nuovo utente con ruolo Editor e usa quello

## Dopo Il Fix

Quando il test mostra **"✓✓✓ UPLOAD SUCCESSFUL! ✓✓✓"**:
- L'app Image Resizer funzionerà perfettamente
- Potrai configurare le credenziali nell'app
- Gli upload saranno automatici senza login interattivo

