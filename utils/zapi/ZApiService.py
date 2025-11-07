import requests
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()

instance_id = os.getenv("ZAPI_INSTANCE_ID")
token = os.getenv("ZAPI_TOKEN")
client_token = os.getenv("ZAPI_CLIENT_TOKEN")

def send_message(message_group, message):
    """
    Realiza o envio de mensagem no WhatsApp

    Args:
        message_group (string): ID do grupo ou telefone a ser enviada a mensagem.
        message (string): Texto a ser enviado.

    Returns:
        Response: Objeto do tipo requests.Response
    """
    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"

    payload = {
        "phone": message_group,
        "message": message
    }

    headers = {
        "Client-Token": client_token,
        "Content-Type": "application/json"
    }

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    return requests.post(url, headers=headers, json=payload, verify=False)
