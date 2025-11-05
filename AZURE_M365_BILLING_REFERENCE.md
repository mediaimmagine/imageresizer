# Azure AD e Microsoft 365 Billing - Guida di Riferimento

## Distinzione tra Fatturazione Microsoft 365 e Azure AD Pay-as-you-go

Le fatture di **Azure AD pay-as-you-go services** sono **separate** dalle fatture di **Microsoft 365**.

### 1. Microsoft 365 Invoicing
- **Cosa include**: Fatture per abbonamenti Microsoft 365 (Office 365, Exchange, SharePoint, Teams, ecc.)
- **Dove accedere**: 
  - Centro di amministrazione di Microsoft 365 → **Billing** → **Bills & payments** (Fatture e pagamenti)
  - URL diretto: https://admin.microsoft.com/AdminPortal/Home#/Billing

### 2. Azure AD Pay-as-you-go Services
- **Cosa include**: Servizi Azure e Azure AD con consumo/fatturazione a consumo
- **Dove accedere**: 
  - **Portale Azure** (portal.azure.com) - **NON** nel Centro di amministrazione di Microsoft 365
  - URL diretto: https://portal.azure.com/#blade/Microsoft_Azure_Billing/BillingMenuBlade/bills

---

## Permessi Necessari

### Per Microsoft 365 Invoicing

Ruoli disponibili (nel **Centro di amministrazione di Microsoft 365**):

1. **Billing Administrator** (Amministratore fatturazione) - ⭐ CONSIGLIATO
   - Accesso completo a billing e fatturazione
   - Non può modificare altre impostazioni amministrative

2. **Global Reader** (Lettore globale) - ⭐ SOLO LETTURA
   - Può visualizzare tutte le fatture e report
   - Non può modificare nulla

3. **Global Administrator** (Amministratore globale)
   - Accesso completo (usare con cautela)

**Come assegnare (M365 Admin Center):**
1. **Utenti** → **Utenti attivi**
2. Seleziona l'utente → **Gestisci ruoli**
3. Seleziona **Billing Administrator** o **Lettore globale**

**Oppure:**
1. **Azure Active Directory** → **Ruoli e amministratori**
2. Cerca "Billing Administrator" o "Lettore globale"
3. Assegna il ruolo all'utente

---

### Per Azure AD Pay-as-you-go Services (Portale Azure)

Ruoli necessari nel **Portale Azure**:

1. **Billing Reader** (Lettore fatturazione) - ⭐ CONSIGLIATO PER SOLA LETTURA
   - Solo visualizzazione delle fatture Azure
   - Non può modificare nulla

2. **Cost Management Reader** (Lettore gestione costi)
   - Visualizza costi e fatture Azure

3. **Owner** o **Contributor** a livello di sottoscrizione
   - Più poteri (non necessario solo per le fatture)

4. **Global Administrator** o **User Administrator**
   - Può gestire ruoli anche in Azure

**Come assegnare (Portale Azure):**

**Metodo 1 - Tramite Sottoscrizione:**
1. Vai a **portal.azure.com**
2. **Sottoscrizioni** → Seleziona la sottoscrizione
3. **Controllo di accesso (IAM)**
4. **Aggiungi** → **Aggiungi assegnazione di ruolo**
5. Seleziona **Billing Reader** (Lettore fatturazione)
6. Assegna all'utente

**Metodo 2 - Tramite Cost Management:**
1. **Cost Management + Billing**
2. **Access control (IAM)**
3. **Aggiungi** → **Aggiungi assegnazione di ruolo**
4. Assegna **Billing Reader**

---

## Accesso alle Fatture

### Microsoft 365 Fatture
- **Centro di amministrazione di Microsoft 365**: https://admin.microsoft.com
- **Billing** → **Bills & payments**
- Oppure: https://admin.microsoft.com/AdminPortal/Home#/Billing

### Azure Fatture
- **Portale Azure**: https://portal.azure.com
- **Cost Management + Billing** → **Bills** (Fatture)
- Oppure: https://portal.azure.com/#blade/Microsoft_Azure_Billing/BillingMenuBlade/bills

---

## Best Practices

1. **Microsoft 365**: Usa **Billing Administrator** per accesso completo o **Global Reader** per sola lettura
2. **Azure**: Usa **Billing Reader** per sola visualizzazione delle fatture Azure
3. **Evita** di assegnare **Global Administrator** solo per vedere le fatture
4. I due sistemi di fatturazione sono **completamente separati** - servono permessi diversi

---

## Note Importanti

- ⚠️ **Global Reader** (M365) non dà accesso alle fatture Azure - serve **Billing Reader** nel Portale Azure
- ⚠️ Le fatture Azure sono accessibili solo dal **Portale Azure**, non dal Centro di amministrazione di Microsoft 365
- ⚠️ Se un utente vede le fatture M365 ma non quelle Azure, è perché manca il ruolo **Billing Reader** nel Portale Azure

---

## Nomi Ruoli in Italiano

- **Global Reader** = **Lettore globale**
- **Billing Administrator** = **Amministratore fatturazione**
- **Billing Reader** = **Lettore fatturazione**
- **Global Administrator** = **Amministratore globale**
- **Cost Management Reader** = **Lettore gestione costi**

---

*Documento creato: $(date)*
*Aggiornato per distinguere tra Microsoft 365 e Azure AD pay-as-you-go billing*




