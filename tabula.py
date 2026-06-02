import yaml
import json
import requests
import os
from src.cli import define_arguments
from dotenv import load_dotenv

MONTHS = {
    1 : "Gennaio",
    2 : "Febbraio",
    3 : "Marzo",
    4 : "Aprile",
    5 : "Maggio",
    6 : "Giugno",
    7 : "Luglio",
    8 : "Agosto",
    9 : "Settembre",
    10 : "Ottobre",
    11 : "Novembre",
    12 : "Dicembre",
}

def get_dates_line(start_date_str:str, end_date_str:str) -> str :
    start_date = list(map(int, start_date_str.split('-')))
    end_date = list(map(int, end_date_str.split('-')))

    date_range : str = ""
    if start_date[1] == end_date[1]:
        return f"_Dal {start_date[2]} al {end_date[2]} {MONTHS[end_date[1]]}_"
    else:
        return f"_Dal {start_date[2]} {MONTHS[start_date[1]]} al {end_date[2]} {MONTHS[end_date[1]]}_"

def telegram_bot_send(token:str, chat_id:str, message:str) -> requests.Response :
    # Prepare message
    message_e = message.replace('-','\\-')
    message_e = message_e.replace('.','\\.')
    message_e = message_e.replace('[','\\[')
    message_e = message_e.replace(']','\\]')

    url = f"https://api.telegram.org/bot{token}/sendMessage"    
    payload = {
        "chat_id": chat_id,
        "text": message_e,
        "parse_mode": "MarkdownV2",
        "disable_notification": True
    }
    return requests.post(url, json=payload)

def assembly_message(header:str|None, dates_line:str|None, footer:str|None, days: list) -> str :
    message = ""
    if header: message = f"{header}\n"
    if dates_line: message = f"{message}{dates_line}\n\n"
    for entry in days:
        message = f"{message}{entry}\n\n"
    if footer: message = f"{message}{footer}"
    return message

def get_first_line_to_send(calendar_file:str) -> dict | None :
    with open(calendar_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_to_send = line
            json_to_send = json.loads(line_to_send)
            if not json_to_send['inviato']:
                return {"json": json_to_send, "string": line_to_send.strip('\n')}
    return None

def update_calendar(calendar_file: str, to_send: dict, message_id: str) -> bool:
    to_send['json']['inviato'] = True
    to_send['json']['message_id'] = message_id
    lines_to_write = []
    try:
        with open(calendar_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip('\n') == to_send['string']:
                    line = json.dumps(to_send['json'])
                lines_to_write.append(line.strip('\n') + '\n')

        with open(calendar_file, 'w', encoding='utf-8') as f:
            f.writelines(lines_to_write)
        
        return True
    except:
        return False

#####################################################################################################

def main() -> int:
    # Check CLI arguments
    args = define_arguments().parse_args()

    # Load environment from file or OS
    if args.environment:
        load_dotenv(args.environment)
    if not args.dry_run:
        BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
        if not BOT_TOKEN or not CHAT_ID:
            print(f"ERRORE: è necessario definire le variabili d'ambiente")
            return 1
    else:
        print("DRY RUN: non controllo le variabili d'ambiente")

    # Load configuration
    config = None
    if args.more:
        with open(args.more, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

    # Get first non-sent line of calendar
    to_send = get_first_line_to_send(args.calendar_file)
    if not to_send:
        print("Nessun messaggio da inviare.")
        return 0

    # Build message
    message = assembly_message(
        header = config['message']['header'] if config else None,
        dates_line = get_dates_line(to_send['json']['valido-da'], to_send['json']['valido-a']),
        footer = config['message']['footer'] if config else None,
        days = to_send['json']['messaggi']
    )

    # If needed, preview message and ask user confirmation
    if not args.force or args.dry_run:
        print(f"Messaggio da inviare:\n----------------------------------\n{message}\n----------------------------------\n")

        if args.dry_run:
            print("DRY RUN: messaggio non inviato; calendario non aggiornato.")
            return 0

        confirm = input("Inviare questo messaggio? (s/N): ")
        if confirm.lower() == 'n' or confirm == '':
            print("Invio annullato.")
            return 0

    # Send message via Telegram
    response = telegram_bot_send(
        BOT_TOKEN,
        CHAT_ID,
        message
    )
    if not response.ok:
        print("ERRORE: impossibile inviare il messaggio")
        print(f"{response.status_code}:  {response.text}")
        return 1
    # print(f"MESSAGGIO INVIATO:\n{response.text}")
    print("MESSAGGIO INVIATO")

    # Set message as sent
    if not update_calendar(args.calendar_file, to_send, response.json()['result']['message_id']):
        print("ERRORE: impossibile aggiornare il calendario")
        return 1
    
    print(f"CALENDARIO aggiornato")
    return 0

################################################################

if __name__ == "__main__":
    raise SystemExit(main())
