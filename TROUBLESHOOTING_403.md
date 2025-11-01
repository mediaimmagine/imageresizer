# Troubleshooting 403 Error - WP Cerber Security

## Configurazione Completa Richiesta

Per far funzionare l'REST API con WP Cerber, servono **ENTRAMBE** queste impostazioni:

### 1. Consenti per Utenti Registrati
- ✓ **Deve essere ATTIVATO:** "Consenti REST API per utenti registrati" (o simile)
- Questa opzione permette l'autenticazione con Application Password

### 2. Namespace Consenti
- ✓ **Deve contenere:** `wp/v2` nel campo namespace

## Verifica Impostazioni WP Cerber

Vai a **Cerber → Hardening** e verifica:

```
☑ Consenti REST API per utenti registrati  ← DEVE essere spuntato
☑ Disabilita REST API                       ← Può essere spuntato SE hai il namespace

Namespace consentiti:
wp/v2                                      ← DEVE essere presente
```

## Azioni da Fare

### Step 1: Pulisci la Cache
1. **Vai a:** Cerber → Strumenti
2. **Clicca:** "Svuota cache" o "Clear cache"
3. **Oppure:** Disattiva e riattiva WP Cerber temporaneamente

### Step 2: Verifica Entrambe le Impostazioni
Assicurati che siano attive **ENTRAMBE**:
- [x] "Consenti REST API per utenti registrati" = **ATTIVO**
- [x] Namespace `wp/v2` = **PRESENTE**

### Step 3: Verifica Permessi Utente
1. **Vai a:** Utenti → Modifica "COED Image Resizer"
2. **Verifica che il ruolo sia:** Editor o Amministratore
3. **Controlla capacità:** L'utente deve avere `upload_files`

### Step 4: Controlla Log WP Cerber
1. **Vai a:** Cerber → Activity → Log
2. **Cerca:** Richieste bloccate a `/wp-json/wp/v2/media`
3. **Se vedi blocchi:** Clicca su "Whitelist" o "Allow"

### Step 5: Test Rapido
Dopo ogni modifica, testa con:
```bash
python3 test_wp_upload_direct.py
```

## Configurazione Alternativa (se ancora non funziona)

Se dopo tutti questi passaggi ottieni ancora 403:

### Opzione A: Disabilita Completamente il Blocco REST API
1. **Cerber → Hardening**
2. **Rimuovi la spunta da:** "Disabilita REST API"
3. **Salva**

### Opzione B: Aggiungi IP alla Whitelist
1. **Cerber → Access Lists → Whitelist**
2. **Aggiungi:** Il tuo IP pubblico (trovalo su whatismyip.com)
3. **Salva**

### Opzione C: Verifica Altri Plugin di Sicurezza
Alcuni altri plugin potrebbero bloccare:
- Wordfence
- iThemes Security
- All In One WP Security

## Formato Namespace

Assicurati che il namespace sia scritto **esattamente così**:
```
wp/v2
```

**Non:**
- ❌ `/wp/v2`
- ❌ `wp/v2/`
- ❌ `WP/V2`
- ❌ `/wp-json/wp/v2`

## Verifica Finale

Dopo aver fatto tutte le modifiche:
1. **Svuota cache WP Cerber**
2. **Svuota cache WordPress** (se usi plugin cache)
3. **Svuota cache browser** (o prova in incognito)
4. **Esegui test:** `python3 test_wp_upload_direct.py`

## Se Funziona

Quando il test mostra **"✓✓✓ UPLOAD SUCCESSFUL! ✓✓✓"**:
- L'app Image Resizer funzionerà correttamente
- Puoi configurare le credenziali nell'app
- Gli upload funzioneranno automaticamente

