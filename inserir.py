import pandas as pd
from pymongo import MongoClient

# Conexão com o MongoDB Atlas
uri = "mongodb+srv://bismarkkbrito:65EhnC0mmrPlTXzh@cluster0.edzozwq.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)


db = client["IDH"]  
collection = db["idh"]  

# Ler o arquivo CSV
csv_file = "Desperdício x IDH e População - Food Waste data and research - by country (1).csv"  
df = pd.read_csv(csv_file)

# Converte DataFrame para dicionários 
data = df.to_dict(orient="records")
collection.insert_many(data)

print("Dados inseridos com sucesso")
