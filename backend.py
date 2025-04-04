from typing import Union
from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId 

app = FastAPI()

# Conectar ao MongoDB Atlas
uri = "mongodb+srv://bismarkkbrito:65EhnC0mmrPlTXzh@cluster0.edzozwq.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

# Selecionar banco de dados e coleção
db = client["IDH"]  # Substitua pelo nome do seu banco
collection = db["idh"]  # Substitua pelo nome da coleção



@app.get("/mongo")
def obter_dados():
    dados = []

    # Buscar todos os documentos no MongoDB
    for doc in collection.find():
        doc["_id"] = str(doc["_id"])  # Converter ObjectId para string
        #for k in doc.keys():
            #doc[k] = str(k)

        dados.append(doc)
        
    #print(dados)
    return {"dados": dados}
      
        
    
