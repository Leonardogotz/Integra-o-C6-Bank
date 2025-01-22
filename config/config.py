import os

# Configuração da API do C6
C6_API_URL = "https://api.c6bank.com.br/seu-endpoint"
C6_AUTH_URL = "https://api.c6bank.com.br/oauth/token"

C6_CREDENTIALS = {
    "client_id": os.getenv("C6_CLIENT_ID", "ede8508d-c937-49b6-8949-1aeb3e60dcb9"),
    "client_secret": os.getenv("C6_CLIENT_SECRET", "CZV6AyfvVJHcfyyNqqdIVpINRECMMlGn"),
    "grant_type": "client_credentials"
}

# Configuração da API Zoho
ZOHO_API_URL = "https://www.zohoapis.com/crm/v2/"
ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/token"

ZOHO_CREDENTIALS = {
    "client_id": os.getenv("ZOHO_CLIENT_ID", "1000.FZYBSQLVN9TTP8A5USXOMF5PE32X3W"),
    "client_secret": os.getenv("ZOHO_CLIENT_SECRET", "02de551adab46ce882ce0a439c65da11551474596e"),
    "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN", "1000.91f9dd5c087c37703eb058e69b27887b.a262b27993879b66681830be57e3d4ef"),
    "grant_type": "refresh_token"
}

# Certificados SSL/TLS para C6 Bank (Sem CA Cert)
CERTS = {
    "client_cert": "certs/cert.crt",
    "client_key": "certs/cert.key"
}

# Configuração de logging
LOG_FILE = "logs/app.log"
