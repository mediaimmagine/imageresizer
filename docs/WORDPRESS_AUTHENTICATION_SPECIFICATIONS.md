# WordPress Post Editor - Specifiche di Autenticazione

## 📋 Indice

1. [Panoramica](#panoramica)
2. [Metodi di Autenticazione](#metodi-di-autenticazione)
3. [Configurazione dei Siti](#configurazione-dei-siti)
4. [Dettagli Tecnici](#dettagli-tecnici)
5. [Gestione delle Credenziali](#gestione-delle-credenziali)
6. [Autenticazione per Autore Personalizzato](#autenticazione-per-autore-personalizzato)
7. [Risoluzione Problemi](#risoluzione-problemi)
8. [Sicurezza](#sicurezza)
9. [Modifica Autore di Articoli Esistenti](#modifica-autore-di-articoli-esistenti)

---

## Panoramica

Il **WordPress Post Editor** utilizza due metodi di autenticazione distinti per pubblicare articoli su diversi siti WordPress:

1. **WordPress Application Passwords** - Per siti WordPress standard (Gorizia Oggi, Udine Oggi, Venezia Orientale)
2. **MiniOrange Basic Auth** - Per siti protetti da MiniOrange (Trieste All News)

Entrambi i metodi utilizzano **HTTP Basic Authentication** tramite l'API REST di WordPress (`/wp-json/wp/v2/`).

---

## Metodi di Autenticazione

### 1. WordPress Application Passwords (Standard)

**Siti che utilizzano questo metodo:**
- Gorizia Oggi (`goriziaoggi.news`)
- Udine Oggi (`udineoggi.news`)
- Venezia Orientale (`veneziaorientale.news`)

**Come funziona:**
- Utilizza le **WordPress Application Passwords** (introdotte in WordPress 5.6+)
- Le Application Passwords sono password monouso generate nel profilo utente WordPress
- Non sostituiscono la password principale dell'utente
- Possono essere revocate individualmente senza compromettere l'account principale

**Formato delle credenziali:**
- **Username**: Nome utente WordPress (es. `goriziaNews`, `udineNews`, `redazioneVeneto`)
- **Password**: Application Password generata (formato: `XXXX XXXX XXXX XXXX XXXX XXXX` - 24 caratteri con spazi)

**Esempio:**
```
Username: goriziaNews
Application Password: oNhy TVJx uavO 1bvc f2Ol ts3g
```

**Nota tecnica:** Le Application Passwords vengono inviate senza spazi nel campo password durante l'autenticazione HTTP Basic Auth.

---

### 2. MiniOrange Basic Auth (Trieste All News)

**Siti che utilizzano questo metodo:**
- Trieste All News (`www.triesteallnews.it`)

**Come funziona:**
- Utilizza il plugin **MiniOrange** per l'autenticazione API
- MiniOrange mappa un **Client ID** e un **Client Secret** a un utente WordPress
- L'autenticazione avviene tramite HTTP Basic Auth utilizzando Client ID e Client Secret
- Il Client ID viene utilizzato come username
- Il Client Secret viene utilizzato come password

**Formato delle credenziali:**
- **Username (Client ID)**: Identificativo univoco fornito da MiniOrange (es. `61kgHITprXR2`)
- **Password (Client Secret)**: Chiave segreta fornita da MiniOrange (es. `GZ8706mxMfgMitqVnD3uBpf1`)

**Esempio:**
```
Client ID (Username): 61kgHITprXR2
Client Secret (Password): GZ8706mxMfgMitqVnD3uBpf1
```

**Requisiti MiniOrange:**
- Il Client ID deve essere mappato a un utente WordPress con ruolo **Editor** o **Administrator**
- L'utente deve avere il capability `publish_posts`
- MiniOrange deve essere configurato per consentire l'accesso all'API REST per utenti autenticati

**Nota tecnica:** Per MiniOrange, la password viene inviata così com'è (senza rimuovere spazi, se presenti).

---

## Configurazione dei Siti

### Siti Predefiniti (Hardcoded)

Il programma include 4 siti predefiniti con credenziali hardcoded che non possono essere modificate dall'interfaccia utente:

#### 1. Trieste News
```json
{
  "name": "Trieste News",
  "site_url": "https://www.triesteallnews.it",
  "username": "61kgHITprXR2",
  "app_password": "GZ8706mxMfgMitqVnD3uBpf1",
  "miniorange": true,
  "hardcoded": true
}
```
- **Metodo**: MiniOrange Basic Auth
- **Nota**: Deve utilizzare `www.triesteallnews.it` (con www) per MiniOrange

#### 2. Gorizia Oggi
```json
{
  "name": "Gorizia Oggi",
  "site_url": "https://goriziaoggi.news",
  "username": "goriziaNews",
  "app_password": "oNhy TVJx uavO 1bvc f2Ol ts3g",
  "hardcoded": true
}
```
- **Metodo**: WordPress Application Password
- **Ruolo utente**: COED Post Editor

#### 3. Udine Oggi
```json
{
  "name": "Udine Oggi",
  "site_url": "https://udineoggi.news",
  "username": "udineNews",
  "app_password": "9q7M ioUs j3ov F4WW fUqE h7F7",
  "hardcoded": true
}
```
- **Metodo**: WordPress Application Password

#### 4. Venezia Orientale
```json
{
  "name": "Venezia Orientale",
  "site_url": "https://veneziaorientale.news",
  "username": "redazioneVeneto",
  "app_password": "5wDS wPib mOrP 04do dyYU VAcY",
  "hardcoded": true
}
```
- **Metodo**: WordPress Application Password
- **Ruolo utente**: COED Post Editor

---

## Dettagli Tecnici

### Implementazione HTTP Basic Auth

Tutti i metodi di autenticazione utilizzano **HTTP Basic Authentication** tramite la libreria Python `requests`:

```python
from requests.auth import HTTPBasicAuth

# Per WordPress Application Passwords
clean_password = app_password.replace(" ", "")  # Rimuove spazi
resp = requests.post(
    api_url,
    auth=HTTPBasicAuth(username, clean_password),
    json=post_data,
    headers=headers
)

# Per MiniOrange
clean_password = app_password  # Mantiene password originale
resp = requests.post(
    api_url,
    auth=HTTPBasicAuth(username, clean_password),
    json=post_data,
    headers=headers
)
```

### Headers HTTP

Il programma invia i seguenti headers per tutte le richieste:

```python
headers = {
    'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'X-ImageResizer-Client': 'WordPressPostEditor/1.0'
}
```

**Headers specifici per MiniOrange:**
- `X-ImageResizer-Client`: Identifica il client per MiniOrange
- `X-Requested-With`: Può aiutare con plugin di sicurezza

### Endpoint API Utilizzati

1. **Creazione Post**: `POST /wp-json/wp/v2/posts`
2. **Upload Media**: `POST /wp-json/wp/v2/media`
3. **Ricerca Categorie**: `GET /wp-json/wp/v2/categories?search={name}`
4. **Ricerca Tag**: `GET /wp-json/wp/v2/tags?search={name}`
5. **Creazione Tag**: `POST /wp-json/wp/v2/tags`

### Gestione Redirect

Il programma utilizza `allow_redirects=True` per gestire eventuali redirect di WordPress o MiniOrange:

```python
resp = requests.post(
    api_url,
    auth=HTTPBasicAuth(username, password),
    json=data,
    headers=headers,
    timeout=30,
    allow_redirects=True  # Consente redirect
)
```

---

## Gestione delle Credenziali

### File di Configurazione

Le credenziali vengono salvate in un file JSON condiviso con Image Resizer:

**Percorso**: `~/.imageresizer/wp_settings.json`

**Struttura:**
```json
{
  "sites": [
    {
      "name": "Trieste News",
      "site_url": "https://www.triesteallnews.it",
      "username": "61kgHITprXR2",
      "app_password": "GZ8706mxMfgMitqVnD3uBpf1",
      "miniorange": true,
      "hardcoded": true
    },
    ...
  ],
  "current_index": 0,
  "last_selected_site_indices": [0, 1]
}
```

### Protezione Credenziali Hardcoded

I siti con `"hardcoded": true` hanno le credenziali sempre ripristinate ai valori predefiniti all'avvio del programma, anche se modificate manualmente nel file di configurazione.

**Logica di ripristino:**
```python
# All'avvio, per ogni sito hardcoded:
if default_site.get("hardcoded", False):
    # Trova il sito salvato per URL
    for i, saved_site in enumerate(self.wp_sites):
        if saved_site.get("site_url") == default_site.get("site_url"):
            # Ripristina sempre le credenziali hardcoded
            self.wp_sites[i]["username"] = default_site["username"]
            self.wp_sites[i]["app_password"] = default_site["app_password"]
            self.wp_sites[i]["hardcoded"] = True
```

---

## Autenticazione per Autore Personalizzato

Il programma supporta la pubblicazione con credenziali di autori personalizzati (non l'utente "Redazione").

### Come Funziona

1. L'utente seleziona la checkbox **"Publish as custom author"**
2. Inserisce:
   - **Author Username**: Nome utente WordPress dell'autore
   - **Application Password**: Application Password dell'autore (o Client ID/Secret per MiniOrange)

3. Il programma utilizza queste credenziali invece di quelle del sito per:
   - Pubblicare il post
   - Caricare immagini featured
   - Creare/assegnare categorie e tag

### Firma Autore

Quando si utilizza un autore personalizzato, la firma nell'articolo viene generata dalle iniziali del nome:

- **Nome completo**: "Mario Rossi" → Firma: `[M.R]`
- **Solo nome**: "Mario" → Firma: `[M.M]`
- **Default (Redazione)**: `[Redazione FVG.news COED Assistant]`

### Esempio di Utilizzo

```python
# Durante la pubblicazione
if self.use_custom_author_checkbox.isChecked():
    username = self.custom_author_name_input.text().strip()
    app_password = self.custom_author_password_input.text().strip()
else:
    username = current_site.get("username", "").strip()
    app_password = current_site.get("app_password", "").strip()
```

---

## Risoluzione Problemi

### Errore 401 (Unauthorized)

**Cause comuni:**

1. **Credenziali errate**
   - Verificare username e password
   - Per Application Passwords: verificare che non ci siano spazi extra
   - Per MiniOrange: verificare Client ID e Client Secret

2. **MiniOrange - Authorization header mancante**
   ```
   MISSING_AUTHORIZATION_HEADER
   ```
   - Verificare che MiniOrange sia configurato per accettare REST API
   - Verificare che l'utente mappato abbia ruolo Editor o Administrator

3. **MiniOrange - Permessi insufficienti**
   - Il Client ID è autenticato ma l'utente WordPress mappato non ha `publish_posts`
   - **Soluzione**: Configurare MiniOrange per mappare il Client ID a un utente con ruolo Editor/Administrator

### Errore 403 (Forbidden)

**Cause comuni:**

1. **Plugin di sicurezza** (es. WP Cerber) blocca l'API REST
   - Verificare impostazioni del plugin
   - Aggiungere whitelist per User-Agent o IP

2. **Capability mancanti**
   - L'utente non ha `publish_posts` o `upload_files`
   - Verificare ruolo utente WordPress

### Timeout

**Cause:**
- Connessione lenta
- Server WordPress sovraccarico
- Firewall blocca le richieste

**Soluzione:**
- Aumentare timeout (default: 30 secondi per post, 45 per upload media)
- Verificare connessione di rete

### Redirect Issues

Il programma gestisce automaticamente i redirect con `allow_redirects=True`. Se si verificano problemi:

1. Verificare che l'URL del sito sia corretto (con o senza www)
2. Per MiniOrange: utilizzare sempre `www.triesteallnews.it`

---

## Sicurezza

### Best Practices

1. **Application Passwords**
   - Generare una Application Password dedicata per ogni applicazione
   - Non condividere Application Passwords tra applicazioni
   - Revocare immediatamente se compromessa

2. **MiniOrange Client ID/Secret**
   - Mantenere Client Secret segreto
   - Non committare credenziali in repository Git
   - Ruotare periodicamente le credenziali

3. **File di Configurazione**
   - Il file `~/.imageresizer/wp_settings.json` contiene credenziali in chiaro
   - Proteggere con permessi del filesystem (chmod 600)
   - Non condividere il file tra utenti

4. **HTTPS**
   - Tutti i siti utilizzano HTTPS
   - Le credenziali vengono inviate solo su connessioni cifrate

### Limitazioni di Sicurezza

1. **Credenziali in chiaro nel file JSON**
   - Le credenziali sono salvate in testo piano
   - Il file è protetto solo dai permessi del filesystem

2. **Nessuna crittografia end-to-end**
   - Le credenziali vengono inviate via HTTP Basic Auth (base64 encoded, non cifrato)
   - La sicurezza dipende da HTTPS

3. **Credenziali hardcoded nel codice**
   - Le credenziali predefinite sono hardcoded nel codice sorgente
   - Non è possibile modificarle senza modificare il codice

### Raccomandazioni Future

1. Implementare crittografia per il file di configurazione
2. Utilizzare keychain macOS per memorizzare credenziali
3. Implementare rotazione automatica delle credenziali
4. Aggiungere audit log per tutte le operazioni di autenticazione

---

## Appendice: Codice di Rilevamento Metodo Autenticazione

```python
def _needs_miniorange_auth(self, site_url: str) -> bool:
    """Check if a site needs Miniorange authentication (Trieste)"""
    return "triesteallnews.it" in site_url.lower() or "www.triesteallnews.it" in site_url.lower()
```

**Utilizzo:**
```python
if self._needs_miniorange_auth(site_url):
    clean_password = app_password  # Mantiene password originale
else:
    clean_password = app_password.replace(" ", "")  # Rimuove spazi per Application Passwords
```

---

## Appendice: Esempio di Richiesta API

### Creazione Post (WordPress Application Password)

```python
import requests
from requests.auth import HTTPBasicAuth

site_url = "https://goriziaoggi.news"
username = "goriziaNews"
app_password = "oNhy TVJx uavO 1bvc f2Ol ts3g"

# Rimuovi spazi dalla password
clean_password = app_password.replace(" ", "")

api_url = f"{site_url}/wp-json/wp/v2/posts"

headers = {
    'User-Agent': 'WordPressPostEditor/1.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

post_data = {
    "title": "Titolo Articolo",
    "content": "<p>Contenuto articolo...</p>",
    "status": "draft"
}

response = requests.post(
    api_url,
    auth=HTTPBasicAuth(username, clean_password),
    json=post_data,
    headers=headers,
    timeout=30,
    allow_redirects=True
)

if response.status_code == 201:
    post = response.json()
    print(f"Post creato: ID {post['id']}")
else:
    print(f"Errore: {response.status_code} - {response.text}")
```

### Creazione Post (MiniOrange)

```python
site_url = "https://www.triesteallnews.it"
client_id = "61kgHITprXR2"
client_secret = "GZ8706mxMfgMitqVnD3uBpf1"

# Per MiniOrange, mantieni password originale
clean_password = client_secret

api_url = f"{site_url}/wp-json/wp/v2/posts"

headers = {
    'User-Agent': 'WordPressPostEditor/1.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-ImageResizer-Client': 'WordPressPostEditor/1.0'
}

post_data = {
    "title": "Titolo Articolo",
    "content": "<p>Contenuto articolo...</p>",
    "status": "draft"
}

response = requests.post(
    api_url,
    auth=HTTPBasicAuth(client_id, clean_password),
    json=post_data,
    headers=headers,
    timeout=30,
    allow_redirects=True
)

if response.status_code == 201:
    post = response.json()
    print(f"Post creato: ID {post['id']}")
else:
    print(f"Errore: {response.status_code} - {response.text}")
```

---

## Modifica Autore di Articoli Esistenti

### È Possibile Modificare l'Autore?

**Sì**, è possibile modificare l'autore di un articolo già pubblicato tramite WordPress REST API utilizzando l'endpoint di aggiornamento.

### Come Funziona

WordPress REST API supporta la modifica del campo `author` di un post esistente tramite:

- **Endpoint**: `PUT /wp-json/wp/v2/posts/{id}` o `POST /wp-json/wp/v2/posts/{id}`
- **Campo**: `author` (ID numerico dell'utente WordPress)
- **Metodo**: HTTP PUT o POST con autenticazione

### Requisiti

1. **Permessi**: L'utente autenticato deve avere il capability `edit_others_posts` (tipicamente Editor o Administrator)
2. **ID Autore**: È necessario conoscere l'ID numerico dell'utente WordPress che diventerà il nuovo autore
3. **ID Post**: È necessario conoscere l'ID del post da modificare

### Esempio di Implementazione

```python
import requests
from requests.auth import HTTPBasicAuth

def change_post_author(site_url: str, username: str, app_password: str, 
                      post_id: int, new_author_id: int) -> bool:
    """
    Modifica l'autore di un post esistente.
    
    Args:
        site_url: URL del sito WordPress
        username: Username o Client ID per autenticazione
        app_password: Application Password o Client Secret
        post_id: ID del post da modificare
        new_author_id: ID numerico del nuovo autore WordPress
    
    Returns:
        True se la modifica è riuscita, False altrimenti
    """
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    
    # Pulisci password (rimuovi spazi per Application Passwords)
    if "triesteallnews.it" in site_url.lower():
        clean_password = app_password  # MiniOrange: mantieni originale
    else:
        clean_password = app_password.replace(" ", "")  # WordPress: rimuovi spazi
    
    headers = {
        'User-Agent': 'WordPressPostEditor/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-ImageResizer-Client': 'WordPressPostEditor/1.0'
    }
    
    # Payload con solo il campo author modificato
    update_data = {
        "author": new_author_id
    }
    
    try:
        response = requests.post(
            api_url,
            auth=HTTPBasicAuth(username, clean_password),
            json=update_data,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            updated_post = response.json()
            print(f"✓ Autore modificato con successo!")
            print(f"  Post ID: {updated_post['id']}")
            print(f"  Nuovo autore ID: {updated_post['author']}")
            return True
        else:
            print(f"✗ Errore: HTTP {response.status_code}")
            print(f"  Risposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Errore durante la modifica: {e}")
        return False
```

### Come Ottenere l'ID Autore

Per ottenere l'ID numerico di un utente WordPress:

```python
def get_user_id_by_username(site_url: str, username: str, app_password: str, 
                            target_username: str) -> Optional[int]:
    """
    Ottiene l'ID numerico di un utente WordPress dal suo username.
    
    Args:
        site_url: URL del sito WordPress
        username: Username per autenticazione
        app_password: Application Password
        target_username: Username dell'utente di cui si vuole l'ID
    
    Returns:
        ID numerico dell'utente, o None se non trovato
    """
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/users"
    
    clean_password = app_password.replace(" ", "")
    
    headers = {
        'User-Agent': 'WordPressPostEditor/1.0',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(username, clean_password),
            params={"search": target_username, "per_page": 100},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get("slug") == target_username or user.get("name") == target_username:
                    return user.get("id")
        return None
    except Exception as e:
        print(f"Errore: {e}")
        return None
```

### Esempio Completo

```python
# Configurazione
site_url = "https://goriziaoggi.news"
username = "goriziaNews"
app_password = "oNhy TVJx uavO 1bvc f2Ol ts3g"
post_id = 12345  # ID del post da modificare
new_author_username = "marioRossi"  # Username del nuovo autore

# 1. Ottieni ID del nuovo autore
new_author_id = get_user_id_by_username(
    site_url, username, app_password, new_author_username
)

if not new_author_id:
    print(f"✗ Utente '{new_author_username}' non trovato")
else:
    # 2. Modifica autore del post
    success = change_post_author(
        site_url, username, app_password, post_id, new_author_id
    )
    
    if success:
        print(f"✓ Autore modificato: {new_author_username} (ID: {new_author_id})")
```

### Limitazioni e Note

1. **Permessi**: Solo Editor e Administrator possono modificare l'autore di post di altri utenti
2. **MiniOrange**: Funziona anche con MiniOrange se l'utente mappato ha i permessi necessari
3. **Storico**: La modifica dell'autore non modifica lo storico del post (revisioni, date, ecc.)
4. **Firma**: La firma nell'articolo (`[M.R]`) non viene aggiornata automaticamente - è parte del contenuto HTML

### Implementazione Futura

Per aggiungere questa funzionalità al WordPress Post Editor, si potrebbe:

1. Aggiungere un campo "Post ID" per caricare un post esistente
2. Aggiungere un dropdown per selezionare il nuovo autore
3. Implementare la funzione `change_post_author()` nel codice
4. Aggiungere un pulsante "Update Author" nell'interfaccia

---

## Changelog

- **v1.0** (2024): Implementazione iniziale con supporto per WordPress Application Passwords e MiniOrange Basic Auth
- Supporto multi-sito
- Supporto autori personalizzati
- Credenziali hardcoded per siti predefiniti
- **v1.1** (2024-11-21): Aggiunta documentazione per modifica autore post esistenti

---

**Documento creato il:** 2024-11-21  
**Ultimo aggiornamento:** 2024-11-21  
**Versione programma:** WordPress Post Editor 1.0  
**Autore:** COED Digital Editor - mediaimmagine s.r.l.

