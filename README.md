![CI](https://github.com/Rabzael/TabulaBot/actions/workflows/ci.yml/badge.svg) ![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![Send scheduled message](https://github.com/Rabzael/TabulaBot/actions/workflows/send.yml/badge.svg)

# TabulaBot

Script Python per comporre e inviare su Telegram messaggi calendarizzati, a partire da un calendario JSONL e, opzionalmente, da una configurazione YAML per header e footer. Include anche una piccola UI Streamlit per modificare i file JSONL prima dell'invio schedulato.

Python script to compose and send scheduled Telegram messages, using a JSONL calendar and, optionally, a YAML configuration file for header and footer. It also includes a small Streamlit UI to edit JSONL files before scheduled sending.

**In produzione** dal 2026: invia aggiornamenti settimanali reali su un canale Telegram ogni giovedì mattina tramite GitHub Actions schedulato — non è una demo.
**In production** since 2026: sends real weekly updates to a Telegram channel every Thursday morning via a scheduled GitHub Actions workflow — not a demo.

🇮🇹 [Italiano](#italiano) | 🇬🇧 [English](#english)

---

## Italiano

### Punti tecnici

- Applicazione CLI in Python.
- Calendario JSONL usato come sorgente dati append-friendly.
- Configurazione YAML opzionale separata dai dati del calendario.
- Gestione dei secret tramite variabili d'ambiente.
- Integrazione con Telegram Bot API.
- UI Streamlit per modificare i calendari JSONL.
- Modalita `--dry-run` per validare il messaggio senza effetti collaterali.
- Tracciamento dello stato di invio tramite `inviato` e `message_id`.
- Blocco dell'invio se il messaggio contiene marker di verifica.
- Schedulazione tramite GitHub Actions.

### Uso dell'AI

L'AI e stata usata come supporto allo sviluppo per revisione del codice, documentazione, progettazione dei test e rifinitura della struttura del progetto.

Nell'uso in produzione puo essere impiegata anche come supporto alla preparazione del calendario JSONL, mantenendo comunque una revisione manuale prima dell'invio dei messaggi.

### Come funziona

```text
Calendario JSONL
      |
Configurazione YAML opzionale + variabili d'ambiente
      |
tabula.py
      |
Telegram Bot API
      |
Canale o chat Telegram
```

`tabula.py` legge il primo elemento del calendario con `inviato: false`, genera il messaggio, chiede conferma e lo invia tramite Telegram. Se viene passato `--more`, aggiunge header e footer dal file YAML. Dopo l'invio aggiorna la riga del calendario impostando `inviato: true` e salvando il `message_id` restituito da Telegram.

`ui.py` e separato dal flusso di invio: serve solo a scegliere e modificare un file JSONL. Lo script `tabula.py` resta il punto di ingresso per invio manuale o schedulato.

### Requisiti

- Python 3
- Un bot Telegram
- Un `chat_id` Telegram valido
- Un `chat_id` personale opzionale per ricevere avvisi quando un invio viene bloccato

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

### File di esempio

La cartella `examples` contiene modelli pronti da copiare o adattare:

- `examples/calendario.jsonl`: calendario in formato JSONL
- `examples/tabula.yaml`: configurazione opzionale di header e footer
- `examples/.env.example`: variabili d'ambiente richieste

### Esempio di messaggio renderizzato

Partendo da `examples/calendario.jsonl` ed `examples/tabula.yaml`, questo è il messaggio così come appare nella chat Telegram (grassetto e corsivo già interpretati da Telegram, non i marker Markdown grezzi):

> **Aggiornamenti settimanali**
> _Dal 7 al 13 Giugno_
>
> **Lunedi 8/06 - Stand-up team prodotto**
> 9:30 - Canale operativo
>
> **Mercoledi 10/06 - Revisione roadmap**
> 15:00 - Sala riunioni virtuale
>
> **Venerdi 12/06 - Report settimanale**
> 17:30 - Invio riepilogo stakeholder
>
> ---
> Per contatti: info@example.org

Generato con:

```bash
python3 tabula.py --dry-run --more examples/tabula.yaml examples/calendario.jsonl
```

### UI per modificare il calendario

Avvia la UI con:

```bash
streamlit run ui.py
```

All'avvio compare solo il selettore del file calendario. La UI cerca file `.jsonl` nelle cartelle `data/` ed `examples/`. Dopo la selezione mostra l'elenco dei periodi e l'editor del testo.

Nell'editor, una riga vuota separa i blocchi di messaggio. I blocchi vuoti vengono scartati al salvataggio:

```text
Messaggio 1

Messaggio 2
```

viene salvato come:

```json
"messaggi": ["Messaggio 1", "Messaggio 2"]
```

La UI non invia messaggi Telegram e non richiede token.

### Configurazione YAML opzionale

Esempio:

```yaml
message:
  header: "*Aggiornamenti settimanali*"
  footer: "---\nPer contatti: info@example.org"
```

Campi usati dallo script quando viene passata l'opzione `--more`:

- `message.header`: intestazione del messaggio Telegram
- `message.footer`: testo finale del messaggio Telegram

### Calendario JSONL

Ogni riga del file calendario è un oggetto JSON indipendente.

```json
{"inviato": false, "valido-da": "2026-06-07", "valido-a": "2026-06-13", "messaggi": ["*Lunedi 8/06 - Stand-up team prodotto*\n9:30 - Canale operativo\n\n*Mercoledi 10/06 - Revisione roadmap*\n15:00 - Sala riunioni virtuale"]}
```

Campi:

- `inviato`: `false` se il messaggio deve ancora essere inviato, `true` dopo l'invio
- `valido-da`: data di inizio validita nel formato `YYYY-MM-DD`
- `valido-a`: data di fine validita nel formato `YYYY-MM-DD`
- `messaggi`: elenco dei blocchi di testo da inserire nel messaggio
- `fsspx`: elenco opzionale di righe (es. messe FSSPX) mostrate in una sezione a parte in fondo al messaggio, prima del footer, precedute dalla riga `Per completezza segnaliamo:`
- `message_id`: identificativo Telegram del messaggio inviato, aggiunto o aggiornato dallo script

Se un blocco in `messaggi` o in `fsspx` contiene il marker `???`, l'invio viene bloccato. In questo caso il messaggio non viene pubblicato sul canale Telegram.

### Variabili d'ambiente

Lo script richiede:

```env
TELEGRAM_BOT_TOKEN=1234567890:AAExampleTokenDaSostituire
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_ALERT_CHAT_ID=123456789
```

`TELEGRAM_ALERT_CHAT_ID` e opzionale ma consigliato per l'esecuzione schedulata: se un invio viene bloccato dalla validazione, il bot invia un messaggio di avviso a quella chat privata. Per ricevere messaggi privati dal bot, devi prima aprire Telegram e scrivere al bot almeno una volta.

Puoi caricarle da file con l'opzione `-e`:

```bash
python3 tabula.py -e examples/.env.example --more examples/tabula.yaml examples/calendario.jsonl
```

Per verificare il messaggio senza inviarlo e senza modificare il calendario:

```bash
python3 tabula.py --dry-run examples/calendario.jsonl
```

Per includere header e footer dal file YAML:

```bash
python3 tabula.py --dry-run --more examples/tabula.yaml examples/calendario.jsonl
```

Per inviare senza richiesta di conferma:

```bash
python3 tabula.py -f -e config/.env.dev --more config/tabula.yaml data/2026.jsonl
```

Non pubblicare token reali o file `.env` privati nel repository.

### Invio schedulato con GitHub Actions

Il workflow `.github/workflows/send.yml` esegue l'invio ogni giovedi mattina:

- `06:00 UTC`, cioe `08:00` in Italia durante l'ora legale e `07:00` in inverno
- usa `config/tabula.yaml` e `data/2026.jsonl`
- dopo un invio riuscito committa il calendario aggiornato con `inviato: true` e `message_id`

Configura questi secret in GitHub, in `Settings > Secrets and variables > Actions`:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
TELEGRAM_ALERT_CHAT_ID
```

### Roadmap / TODO

- Validazione esplicita dei file JSONL/YAML con messaggi di errore chiari.
- Scrittura atomica del calendario per ridurre il rischio di corruzione del file durante l'aggiornamento.
- Miglioramento dell'escaping MarkdownV2 per Telegram.
- Link dinamico alla configurazione YAML, per poter richiamare oggetti definiti nel file YAML all'interno del file JSONL.

## English

### Tech Highlights

- Python CLI application.
- JSONL calendar used as an append-friendly data source.
- Optional YAML configuration separated from calendar data.
- Secret management through environment variables.
- Telegram Bot API integration.
- Streamlit UI to edit JSONL calendars.
- `--dry-run` mode to validate messages without side effects.
- Delivery state tracking through `inviato` and `message_id`.
- Sending is blocked when the message contains review markers.
- Scheduled execution through GitHub Actions.

### AI Usage

AI was used as a development assistant for code review, documentation, test design, and project structure refinement.

In production usage, it may also support the preparation of the JSONL calendar, with manual review before messages are sent.

### How It Works

```text
JSONL calendar
      |
Optional YAML configuration + environment variables
      |
tabula.py
      |
Telegram Bot API
      |
Telegram channel or chat
```

`tabula.py` reads the first calendar entry with `inviato: false`, builds the Telegram message, asks for confirmation, and sends it through the Telegram Bot API. When `--more` is provided, it adds header and footer from the YAML file. After a successful send, it updates the calendar line by setting `inviato: true` and storing the Telegram `message_id`.

`ui.py` is separate from the sending flow: it only selects and edits a JSONL file. `tabula.py` remains the entry point for manual or scheduled sending.

### Requirements

- Python 3
- A Telegram bot
- A valid Telegram `chat_id`
- An optional personal `chat_id` to receive alerts when a send is blocked

Install dependencies:

```bash
pip install -r requirements.txt
```

### Example Files

The `examples` directory contains templates that can be copied or adapted:

- `examples/calendario.jsonl`: JSONL calendar
- `examples/tabula.yaml`: optional header and footer configuration
- `examples/.env.example`: required environment variables

### Rendered Message Example

Starting from `examples/calendario.jsonl` and `examples/tabula.yaml`, this is how the message appears in the Telegram chat (bold and italics already interpreted by Telegram, not the raw Markdown markers):

> **Aggiornamenti settimanali**
> _Dal 7 al 13 Giugno_
>
> **Lunedi 8/06 - Stand-up team prodotto**
> 9:30 - Canale operativo
>
> **Mercoledi 10/06 - Revisione roadmap**
> 15:00 - Sala riunioni virtuale
>
> **Venerdi 12/06 - Report settimanale**
> 17:30 - Invio riepilogo stakeholder
>
> ---
> Per contatti: info@example.org

Generated with:

```bash
python3 tabula.py --dry-run --more examples/tabula.yaml examples/calendario.jsonl
```

### Calendar Editing UI

Start the UI with:

```bash
streamlit run ui.py
```

At startup, only the calendar file selector is shown. The UI looks for `.jsonl` files in `data/` and `examples/`. After selecting a file, it shows the period list and text editor.

In the editor, an empty line separates message blocks. Empty blocks are discarded when saving:

```text
Message 1

Message 2
```

is saved as:

```json
"messaggi": ["Message 1", "Message 2"]
```

The UI does not send Telegram messages and does not require tokens.

### Optional YAML Configuration

Example:

```yaml
message:
  header: "*Weekly Updates*"
  footer: "---\nContacts: info@example.org"
```

Fields used by the script when the `--more` option is provided:

- `message.header`: Telegram message header
- `message.footer`: Telegram message footer

### JSONL Calendar

Each line in the calendar file is an independent JSON object.

```json
{"inviato": false, "valido-da": "2026-06-07", "valido-a": "2026-06-13", "messaggi": ["*Monday 8/06 - Product team stand-up*\n9:30 - Operations channel\n\n*Wednesday 10/06 - Roadmap review*\n15:00 - Virtual meeting room"]}
```

Fields:

- `inviato`: `false` if the message still has to be sent, `true` after sending
- `valido-da`: start date in `YYYY-MM-DD` format
- `valido-a`: end date in `YYYY-MM-DD` format
- `messaggi`: list of text blocks to include in the message
- `fsspx`: optional list of lines (e.g. FSSPX Masses) shown in a separate section at the end of the message, before the footer, preceded by the line `Per completezza segnaliamo:`
- `message_id`: Telegram message identifier, added or updated by the script

If a block in `messaggi` or `fsspx` contains the `???` marker, sending is blocked. In that case, the message is not published to the Telegram channel.

### Environment Variables

The script requires:

```env
TELEGRAM_BOT_TOKEN=1234567890:AAExampleTokenToReplace
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_ALERT_CHAT_ID=123456789
```

`TELEGRAM_ALERT_CHAT_ID` is optional but recommended for scheduled runs: if a send is blocked by validation, the bot sends an alert message to that private chat. To receive private messages from the bot, you must first open Telegram and send the bot at least one message.

Load them from a file with `-e`:

```bash
python3 tabula.py -e examples/.env.example --more examples/tabula.yaml examples/calendario.jsonl
```

Preview the message without sending it or updating the calendar:

```bash
python3 tabula.py --dry-run examples/calendario.jsonl
```

Include header and footer from the YAML file:

```bash
python3 tabula.py --dry-run --more examples/tabula.yaml examples/calendario.jsonl
```

Send without confirmation:

```bash
python3 tabula.py -f -e config/.env.dev --more config/tabula.yaml data/2026.jsonl
```

Do not publish real tokens or private `.env` files in the repository.

### Scheduled Sending With GitHub Actions

The `.github/workflows/send.yml` workflow runs the sender every Thursday morning:

- `06:00 UTC`, which is `08:00` in Italy during daylight saving time and `07:00` in winter
- uses `config/tabula.yaml` and `data/2026.jsonl`
- after a successful send, commits the updated calendar with `inviato: true` and `message_id`

Configure these secrets in GitHub, under `Settings > Secrets and variables > Actions`:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
TELEGRAM_ALERT_CHAT_ID
```

### Roadmap / TODO

- Explicit JSONL/YAML validation with clear error messages.
- Atomic calendar writes to reduce the risk of corrupting the file during updates.
- Improved MarkdownV2 escaping for Telegram.
