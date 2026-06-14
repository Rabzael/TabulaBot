import json

def load_json_calendar(calendar_file:str) -> list[dict]:
  with open(calendar_file, 'r', encoding='utf-8') as f:
    return [json.loads(line) for line in f if line.strip()]

def get_first_line_to_send(calendar:list) -> int | None :
  for index, line in enumerate(calendar):
    if not line.get('inviato', False):
      return index
  return None

def update_calendar(calendar_file: str, to_update: list) -> bool:
  try:
    with open(calendar_file, mode="w", encoding="utf-8") as f:
        for entry in to_update:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")  
    return True
  except Exception as e:
    print(f'ERROR: {e}')
    return False
