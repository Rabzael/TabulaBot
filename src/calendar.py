import json

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