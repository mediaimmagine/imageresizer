# WP Cerber Security - Configurazione in Italiano

## Impostazione Namespace REST API

Quando WP Cerber ha l'opzione:
**"Specificare gli spazi dei nomi REST API da consentire quando l'API REST è disabilitata. Uno spazio dei nomi per riga."**

### Soluzione: Aggiungi questi namespace

Nel campo di testo, aggiungi (uno per riga):

```
wp/v2
```

Oppure, se vuoi essere più specifico per il media endpoint:

```
wp/v2/media
```

### Spiegazione

- **`wp/v2`** è il namespace principale dell'API REST di WordPress v2
- Include tutti gli endpoint come:
  - `/wp-json/wp/v2/media` (per upload immagini)
  - `/wp-json/wp/v2/posts`
  - `/wp-json/wp/v2/users`
  - ecc.

### Configurazione Completa

1. **Vai a:** Dashboard WordPress → Cerber → Hardening
2. **Trova:** "Specificare gli spazi dei nomi REST API da consentire..."
3. **Aggiungi nel campo di testo:**
   ```
   wp/v2
   ```
4. **Salva le modifiche**
5. **Pulisci la cache:** Cerber → Strumenti → Svuota cache (se disponibile)

### Verifica

Dopo aver salvato, testa la connessione:

```bash
python3 test_wp_connection.py
```

O prova direttamente nell'app Image Resizer caricando un'immagine.

### Note Aggiuntive

- **Namespace completo:** `/wp-json/wp/v2/media` → namespace è `wp/v2`
- **Uno per riga:** Se devi aggiungere più namespace, metti uno per riga
- **Case sensitive:** Usa minuscole `wp/v2` non `WP/V2`

