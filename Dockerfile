FROM python:3.9-slim

# Instala as dependências necessárias
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY . .

# Expõe a porta do Flask
EXPOSE 5000

# Executa a aplicação
CMD ["python", "app.py"]
