import requests

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