import requests
import logging
import base64
import os
from config.config import C6_API_URL, C6_AUTH_URL, C6_CREDENTIALS, CERTS

# Cache para token de acesso
c6_access_token_cache = {"token": None}


def get_c6_access_token():
    """Obtém o token de acesso para a API do C6."""
    try:
        response = requests.post(
            C6_AUTH_URL,
            data=C6_CREDENTIALS,
            cert=(CERTS["client_cert"], CERTS["client_key"]),
            verify=True  # Certifique-se de que verify esteja como True
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            c6_access_token_cache["token"] = token
            logging.info("Token de acesso do C6 obtido com sucesso.")
            return token
        else:
            logging.error(f"Erro ao obter token do C6: {response.text}")
            logging.error(f"Status code: {response.status_code}") # Adicione para melhor debug
            raise Exception("Falha na autenticação do C6")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na autenticação do C6: {e}")
        raise


def send_to_c6(data):
    """Envia os dados para a API do C6 e gera o boleto."""
    try:
        # Obtém ou renova o token
        token = c6_access_token_cache.get("token") or get_c6_access_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        # Emite o boleto
        response = requests.post(
            C6_API_URL,
            json=data,
            headers=headers,
            cert=(CERTS["client_cert"], CERTS["client_key"]),
            verify=True  # Ajustar para True em produção
        )

        if response.status_code in [200, 201]:
            logging.info(f"Boleto gerado com sucesso: {response.json()}")
            boleto_id = response.json().get("id")  # ID do boleto retornado
            return consult_boleto(boleto_id, token)  # Consulta o boleto emitido
        elif response.status_code == 401:
            logging.warning("Token expirado, renovando...")
            c6_access_token_cache["token"] = None
            return send_to_c6(data)
        else:
            logging.error(f"Erro na API do C6: {response.text}")
            raise Exception(f"Erro ao gerar boleto: {response.text}")

    except requests.exceptions.SSLError as e:
        logging.error(f"Erro de certificado SSL: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição ao C6: {e}")
        raise


def consult_boleto(boleto_id, token):
    """Consulta os detalhes de um boleto na API do C6."""
    try:
        url = f"{C6_API_URL}/{boleto_id}"  # Endpoint para consultar boletos
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            url,
            headers=headers,
            cert=(CERTS["client_cert"], CERTS["client_key"]),
            verify=True  # Ajustar para True em produção
        )

        if response.status_code == 200:
            boleto_data = response.json()
            logging.info(f"Boleto consultado com sucesso: {boleto_data}")
            return boleto_data  # Retorna os detalhes do boleto
        else:
            logging.error(f"Erro ao consultar boleto: {response.text}")
            raise Exception(f"Erro ao consultar boleto: {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao consultar boleto no C6: {e}")
        raise

def decode_boleto_pdf(base64_pdf, pdf_path):
    """Decodifica o PDF em Base64 e salva no caminho especificado."""
    try:
        decoded_pdf = base64.b64decode(base64_pdf)
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(decoded_pdf)
        logging.info(f"PDF do boleto salvo em {pdf_path}.")
        return pdf_path
    except Exception as e:
        logging.exception(f"Erro ao decodificar e salvar o PDF: {e}")
        raise