from flask import Flask, request, jsonify, abort
import logging
from services.auth_c6_service import send_to_c6, decode_boleto_pdf, get_c6_access_token
from services.auth_zoho_service import get_zoho_access_token, upload_attachment_to_zoho
import os
import pathlib
import requests
from config.config import CERTS, ZOHO_API_URL # Adicione esta linha

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

@app.route('/zoho-webhook', methods=['POST'])
def receive_zoho_data():
    temp_dir = pathlib.Path("temp_files")
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        logging.info(f"Recebido JSON do Zoho: {data}")

        # Validação e tratamento de dados do Zoho - MELHORADO
        try:
            boleto_data = {
                "external_reference_id": data["external_reference_id"],
                "amount": float(data["amount"]),
                "due_date": data["due_date"],
                "instructions": [str(ins) for ins in data.get("instructions", [])], # Lista de strings
                "payer": {
                    "name": data["payer"]["name"],
                    "tax_id": data["payer"]["tax_id"],
                    "email": data["payer"]["email"],
                    "address": {
                        "street": data["payer"]["address"]["street"],
                        "number": int(data["payer"]["address"]["number"]),
                        "complement": data["payer"]["address"]["complement"],
                        "city": data["payer"]["address"]["city"],
                        "state": data["payer"]["address"]["state"],
                        "zip_code": data["payer"]["address"]["zip_code"],
                    }
                }
            }

            # Verificação de campos obrigatórios (adicione mais conforme necessário)
            required_fields = ["external_reference_id", "amount", "due_date", "payer", "payer.name", "payer.tax_id", "payer.email", "payer.address"]
            for field in required_fields:
                if "." in field:
                    nested_fields = field.split(".")
                    current_level = data
                    for f in nested_fields:
                        if f not in current_level:
                            raise ValueError(f"Campo obrigatório '{field}' está faltando.")
                        current_level = current_level[f]
                    if not current_level:
                        raise ValueError(f"Campo obrigatório '{field}' está vazio.")
                else:
                    if field not in data or not data[field]:
                        raise ValueError(f"Campo obrigatório '{field}' está faltando ou vazio.")

            # Verificação de tipos de dados (adicione mais conforme necessário)
            if not isinstance(boleto_data["amount"], (int, float)):
                raise ValueError("O campo 'amount' deve ser um número.")
            if not isinstance(boleto_data["payer"]["address"]["number"], int):
                raise ValueError("O campo 'payer.address.number' deve ser um número inteiro.")
            if not isinstance(boleto_data["instructions"], list):
                raise ValueError("O campo 'instructions' deve ser uma lista.")
            for instruction in boleto_data["instructions"]:
                if not isinstance(instruction, str):
                    raise ValueError("Todos os itens em 'instructions' devem ser strings.")


        except (KeyError, ValueError) as e:
            logging.error(f"Dados inválidos do Zoho: {e}")
            return jsonify({"error": f"Dados inválidos do Zoho: {e}"}), 400

        # Gera o boleto no C6 (inclui emissão e consulta)
        boleto_response = send_to_c6(boleto_data)

        # Decodifica o PDF do boleto retornado
        pdf_base64 = boleto_response.get("base64_pdf_file")
        boleto_id = boleto_response.get("id")
        pdf_filename = f"{boleto_id}.pdf"
        pdf_path = temp_dir / pdf_filename

        # Chamada única e CORRETA para decode_boleto_pdf
        decode_boleto_pdf(pdf_base64, pdf_path)

        # Faz o upload do PDF para a fatura no Zoho
        zoho_token = get_zoho_access_token()
        invoice_id = data.get("invoice_id")
        upload_attachment_to_zoho(invoice_id, pdf_path, zoho_token, boleto_id)

        # Remove o arquivo PDF após o upload
        os.remove(pdf_path)

        return jsonify({"message": "Boleto gerado e anexado com sucesso"}), 200

    except Exception as e:
        logging.exception(f"Erro no processamento: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/cancel-boleto', methods=['POST'])
def cancel_boleto():
    try:
        data = request.get_json()
        logging.info(f"Dados recebidos: {data}")

        # Validação dos campos obrigatórios
        required_fields = ["boleto_id", "invoice_id", "document_idBooks"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"O campo '{field}' é obrigatório."}), 400

        boleto_id = data["boleto_id"]
        invoice_id = data["invoice_id"]
        document_id_books = data["document_idBooks"]

        logging.info(f"Boleto ID: {boleto_id}, Invoice ID: {invoice_id}, Document ID Books: {document_id_books}")

        # Consultar o boleto antes de tentar cancelar
        boleto_status = get_boleto_status(boleto_id)
        logging.info(f"Status do boleto: {boleto_status}")

        if boleto_status == "CANCELLED":
            return jsonify({"message": "Boleto já cancelado."}), 200

        # Cancelar o boleto
        response = cancel_boleto_c6(boleto_id)
        response.raise_for_status()

        # Remover o anexo do Zoho (substitua pelo seu código)
        remove_zoho_attachment(invoice_id, document_id_books)

        # Retorna sucesso mesmo sem resposta JSON do C6
        return jsonify({"message": "Boleto cancelado e anexo removido com sucesso"}), 200

    except requests.exceptions.HTTPError as e:
        logging.exception(f"Erro HTTP: {e}")
        abort(e.response.status_code, f"Erro HTTP: {e}")
    except requests.exceptions.RequestException as e:
        logging.exception(f"Erro de rede: {e}")
        abort(500, f"Erro de rede: {e}")
    except KeyError as e:
        logging.exception(f"Campo faltando na requisição: {e}")
        abort(400, f"Campo faltando na requisição: {e}")
    except Exception as e:
        logging.exception(f"Erro inesperado: {e}")
        abort(500, f"Erro inesperado: {e}")


def cancel_boleto_c6(boleto_id):
    token = get_c6_access_token()
    if not token:
        raise Exception("Falha ao obter token de acesso do C6 Bank.")

    url = f"https://baas-api-sandbox.c6bank.info/v1/bank_slips/{boleto_id}/cancel"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.put(url, headers=headers, cert=(CERTS["client_cert"], CERTS["client_key"]), verify=True)
    response.raise_for_status() # Verifica o código de status aqui
    return response # Retorna a resposta, mesmo que seja 204


def get_boleto_status(boleto_id):
    try:
        response = consult_boleto_c6(boleto_id)
        response.raise_for_status()
        return response.json().get("status")
    except requests.exceptions.HTTPError as e:
        logging.exception(f"Erro ao consultar status do boleto: {e}")
        raise  # Re-lance a exceção para ser tratada na função cancel_boleto
    except requests.exceptions.RequestException as e:
        logging.exception(f"Erro de rede ao consultar status do boleto: {e}")
        raise
    except Exception as e:
        logging.exception(f"Erro inesperado ao consultar status do boleto: {e}")
        raise


def consult_boleto_c6(boleto_id):
    token = get_c6_access_token()
    if not token:
        raise Exception("Falha ao obter token de acesso do C6 Bank.")

    url = f"https://baas-api-sandbox.c6bank.info/v1/bank_slips/{boleto_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, cert=(CERTS["client_cert"], CERTS["client_key"]), verify=True)
    return response


def remove_zoho_attachment(invoice_id, document_id_books):
    # Substitua este comentário pelo seu código para remover o anexo do Zoho
    zoho_access_token = get_zoho_access_token()
    url_zoho = f"{ZOHO_API_URL}/invoices/{invoice_id}/documents/{document_id_books}"
    headers_zoho = {
        "Authorization": f"Zoho-oauthtoken {zoho_access_token}"
    }
    response_zoho = requests.delete(url_zoho, headers=headers_zoho)
    response_zoho.raise_for_status()
    logging.info(f"Anexo {document_id_books} removido da invoice {invoice_id} com sucesso.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
