# Come Pulire la Cache WP Cerber (Metodi Alternativi)

Se non trovi "Svuota cache" in Strumenti, prova questi metodi:

## Metodo 1: Salvare di Nuovo le Impostazioni
A volte basta salvare di nuovo per applicare le modifiche:

1. **Vai a:** Cerber → Hardening
2. **Verifica** che le impostazioni siano corrette:
   - ☑ "Consenti REST API per utenti registrati" = ATTIVO
   - ☑ Namespace `wp/v2` presente
3. **Clicca:** "Salva modifiche" (anche se non hai cambiato nulla)
4. **Aspetta** qualche secondo
5. **Riprova il test**

## Metodo 2: Disattiva/Riattiva WP Cerber
Questo forza un refresh completo:

1. **Vai a:** Plugin → Plugin installati
2. **Trova:** WP Cerber Security
3. **Clicca:** "Disattiva"
4. **Aspetta** 5 secondi
5. **Clicca:** "Attiva"
6. **Riprova il test**

## Metodo 3: Modifica e Risalva le Impostazioni
Forza WP Cerber a riprocessare le regole:

1. **Vai a:** Cerber → Hardening
2. **Rimuovi temporaneamente** `wp/v2` dal campo namespace
3. **Salva**
4. **Aggiungi di nuovo** `wp/v2`
5. **Salva**
6. **Riprova il test**

## Metodo 4: Cerca "Cache" in Altre Sezioni
La cache potrebbe essere in:
- **Cerber → Settings** → cerca "Cache"
- **Cerber → Dashboard** → cerca "Clear" o "Flush"
- **Cerber → Tools** (Strumenti) → scorri tutte le opzioni
- **Cerber → Activity** → cerca opzioni di pulizia

## Metodo 5: Disabilita Temporaneamente il Blocco REST API
Per testare se è veramente un problema di cache:

1. **Vai a:** Cerber → Hardening
2. **Rimuovi la spunta da:** "Disabilita REST API"
3. **Salva**
4. **Esegui test:** `python3 test_wp_upload_direct.py`
5. **Se funziona:** Il problema era la configurazione/cache
6. **Rimetti la spunta** e aggiungi di nuovo `wp/v2`
7. **Salva**

## Metodo 6: Usa Plugin di Cache (Se Installato)
Se hai un plugin di cache WordPress (WP Super Cache, W3 Total Cache, ecc.):
1. **Vai a** le impostazioni del plugin di cache
2. **Svuota cache lì**
3. Questo a volte aiuta anche con le regole WP Cerber

## Verifica Rapida
Dopo qualsiasi metodo, testa immediatamente:
```bash
python3 test_wp_upload_direct.py
```

## Se Nessun Metodo Funziona
Potrebbe non essere un problema di cache, ma di configurazione:

1. **Verifica** che l'utente "COED Image Resizer" abbia ruolo **Editor** o **Amministratore**
2. **Controlla** Cerber → Activity → Log per vedere se le richieste sono ancora bloccate
3. **Prova** a disabilitare completamente "Disabilita REST API" per verificare se funziona senza restrizioni

