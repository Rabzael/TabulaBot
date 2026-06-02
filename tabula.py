import yaml
import os
from src.cli import define_arguments
from src.calendar import get_first_line_to_send, update_calendar
from src.telegram import telegram_bot_send
from src.message import assembly_message, get_dates_line

from dotenv import load_dotenv

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
