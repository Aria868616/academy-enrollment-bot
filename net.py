import requests
import config

response = requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe")
print(response.json())