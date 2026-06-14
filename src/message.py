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

BLOCKED_MARKERS = ['???']

def validate_messages(messaggi:list[str]) -> list[str]:
  invalid_messages = []
  for msg in messaggi:
    for marker in BLOCKED_MARKERS:
      if marker in msg:
        invalid_messages.append(msg)
        continue
  return invalid_messages

def get_dates_line(start_date_str:str, end_date_str:str) -> str :
  start_date = list(map(int, start_date_str.split('-')))
  end_date = list(map(int, end_date_str.split('-')))

  if start_date[1] == end_date[1]:
    return f"_Dal {start_date[2]} al {end_date[2]} {MONTHS[end_date[1]]}_"
  else:
    return f"_Dal {start_date[2]} {MONTHS[start_date[1]]} al {end_date[2]} {MONTHS[end_date[1]]}_"

def assembly_message(header:str|None, dates_line:str|None, footer:str|None, days: list) -> str :
  message = ""
  if header: message = f"{header}\n"
  if dates_line: message = f"{message}{dates_line}\n\n"
  for entry in days:
    message = f"{message}{entry}\n\n"
  if footer: message = f"{message}{footer}"
  return message