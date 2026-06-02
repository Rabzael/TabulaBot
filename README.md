# TabulaBot

Script Python per comporre e inviare su Telegram messaggi calendarizzati, a partire da un calendario JSONL e, opzionalmente, da una configurazione YAML per header e footer.

Python script to compose and send scheduled Telegram messages, using a JSONL calendar and, optionally, a YAML configuration file for header and footer.

## Italiano

### Punti tecnici

- Applicazione CLI in Python.
- Calendario JSONL usato come sorgente dati append-friendly.
- Configurazione YAML opzionale separata dai dati del calendario.
- Gestione dei secret tramite variabili d'ambiente.
- Integrazione con Telegram Bot API.
- Modalita `--dry-run` per validare il messaggio senza effetti collaterali.
- Tracciamento dello stato di invio tramite `inviato` e `message_id`.

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

### Requisiti

- Python 3
- Un bot Telegram
- Un `chat_id` Telegram valido

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

### File di esempio

La cartella `examples` contiene modelli pronti da copiare o adattare:

- `examples/calendario.jsonl`: calendario in formato JSONL
- `examples/tabula.yaml`: configurazione opzionale di header e footer
- `examples/.env.example`: variabili d'ambiente richieste

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
- `message_id`: identificativo Telegram del messaggio inviato, aggiunto o aggiornato dallo script

### Variabili d'ambiente

Lo script richiede:

```env
TELEGRAM_BOT_TOKEN=1234567890:AAExampleTokenDaSostituire
TELEGRAM_CHAT_ID=-1001234567890
```

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

### Roadmap / TODO

- Test unitari con `pytest` per formattazione date, composizione messaggi, selezione della prima riga non inviata, dry-run e aggiornamento calendario.
- Validazione esplicita dei file JSONL/YAML con messaggi di errore chiari.
- Scrittura atomica del calendario per ridurre il rischio di corruzione del file durante l'aggiornamento.
- Exit code coerenti: `0` per successo, `1` per errore.
- Schedulazione tramite GitHub Actions.
- Link dinamico alla configurazione YAML, per poter richiamare oggetti definiti nel file YAML all'interno del file JSONL.

## English

### Tech Highlights

- Python CLI application.
- JSONL calendar used as an append-friendly data source.
- Optional YAML configuration separated from calendar data.
- Secret management through environment variables.
- Telegram Bot API integration.
- `--dry-run` mode to validate messages without side effects.
- Delivery state tracking through `inviato` and `message_id`.

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

### Requirements

- Python 3
- A Telegram bot
- A valid Telegram `chat_id`

Install dependencies:

```bash
pip install -r requirements.txt
```

### Example Files

The `examples` directory contains templates that can be copied or adapted:

- `examples/calendario.jsonl`: JSONL calendar
- `examples/tabula.yaml`: optional header and footer configuration
- `examples/.env.example`: required environment variables

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
- `message_id`: Telegram message identifier, added or updated by the script

### Environment Variables

The script requires:

```env
TELEGRAM_BOT_TOKEN=1234567890:AAExampleTokenToReplace
TELEGRAM_CHAT_ID=-1001234567890
```

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

### Roadmap / TODO

- Explicit JSONL/YAML validation with clear error messages.
- Atomic calendar writes to reduce the risk of corrupting the file during updates.
- Schedule execution with GitHub Actions.
