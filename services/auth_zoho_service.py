import requests
import logging
from config.config import ZOHO_AUTH_URL, ZOHO_CREDENTIALS, ZOHO_API_URL

zoho_access_token_cache = {
    "token": None
}

def get_zoho_access_token():
    """ Obtém e armazena o token OAuth 2.0 da Zoho em cache """

    if zoho_access_token_cache["token"]:
        logging.info("Token de acesso da Zoho ainda é válido.")
        return zoho_access_token_cache["token"]

    logging.info("Solicitando novo token de acesso à Zoho...")

    try:
        response = requests.post(
            ZOHO_AUTH_URL,
            data=ZOHO_CREDENTIALS
        )

        if response.status_code == 200:
            token_data = response.json()
            zoho_access_token_cache["token"] = token_data.get("access_token")
            logging.info("Novo token Zoho armazenado com sucesso.")
            return zoho_access_token_cache["token"]
        else:
            logging.error(f"Erro ao obter token da Zoho: {response.text}")
            raise Exception("Falha ao obter token OAuth Zoho")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na solicitação à Zoho: {e}")
        raise


def upload_attachment_to_zoho(invoice_id, file_path, access_token):
    """Faz o upload de um anexo (PDF) para uma fatura no Zoho Books."""
    try:
        url = f"{ZOHO_API_URL}/invoices/{invoice_id}/attachment"
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

        with open(file_path, "rb") as file:
            files = {"attachment": file}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code in [200, 201]:
            logging.info(f"PDF anexado com sucesso à fatura {invoice_id}.")
        else:
            logging.error(f"Erro ao anexar PDF no Zoho: {response.text}")
            raise Exception(f"Falha ao anexar PDF: {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro no upload para o Zoho: {e}")
        raise