from pymongo import MongoClient

# Configuração da conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.my_library_db  # Nome do banco de dados
collection = db.books      # Nome da coleção (tabela)
