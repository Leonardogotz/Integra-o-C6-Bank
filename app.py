from flask import Flask, request, jsonify
import logging
from services.auth_c6_service import send_to_c6, decode_boleto_pdf
from services.auth_zoho_service import get_zoho_access_token, upload_attachment_to_zoho
import os
import pathlib

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
        pdf_path = decode_boleto_pdf(pdf_base64)

        # Faz o upload do PDF para a fatura no Zoho
        zoho_token = get_zoho_access_token()
        invoice_id = data.get("invoice_id")
        upload_attachment_to_zoho(invoice_id, pdf_path, zoho_token)

        return jsonify({"message": "Boleto gerado e anexado com sucesso"}), 200

    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
