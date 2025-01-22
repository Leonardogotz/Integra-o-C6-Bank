import requests
import logging
from services.auth_c6_service import get_c6_access_token
from config.config import C6_API_URL, CERTS

def send_to_c6(data):
    """ Envia os dados para a API do C6 """
    try:
        token = get_c6_access_token()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(
            C6_API_URL,
            json=data,
            headers=headers,
            cert=(CERTS["client_cert"], CERTS["client_key"]),
            verify=False  # Sem verificação de CA
        )

        logging.info(f"Resposta da API do C6: {response.status_code} {response.text}")

        if response.status_code == 401:
            logging.warning("Token expirado, renovando...")
            c6_access_token_cache["token"] = None
            return send_to_c6(data)

        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao enviar dados para o C6: {e}")
        raise
