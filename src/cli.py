import argparse

def define_arguments() -> argparse.ArgumentParser :
  parser = argparse.ArgumentParser(
      description='Crea e invia messaggi calendarizzati in base alla configurazione fornita.',
      epilog='Esempio: python3 tabula.py --more config.yaml calendario.jsonl'
  )
  parser.add_argument("-f", "--force", action='store_true', help="Non chiede conferma prima di inviare il messaggio")
  parser.add_argument("-e", "--environment", help="File con variabili d'ambiente da caricare. Ha precedenza sulle variabili d'ambiente.", required=False)
  parser.add_argument("-d", "--dry-run", action='store_true', help="Stampa il messaggio ed esce. Non invia né apporta modifiche al file di calendario.")
  parser.add_argument("-m", "--more", help="Path del file con eventuale header/footer", required=False)
  parser.add_argument("calendar_file", help="Path del file calendario")
  return parser
