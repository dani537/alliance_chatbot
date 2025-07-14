from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

def cargar_vectorstore():
    save_dir = Path("src") / "faiss_index"
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = FAISS.load_local(save_dir, embeddings, allow_dangerous_deserialization=True)
    return vectorstore

def clasificar_con_umbral(pregunta_usuario, umbral=0.4):
    # Cargar vectorstore
    vectorstore = cargar_vectorstore()

    # Obtener embedding de la pregunta usando embed_query
    q_emb = vectorstore.embedding_function.embed_query(pregunta_usuario)
    q_emb = np.array([q_emb]).astype('float32')  # Convertir a numpy array 2D

    # Buscar los k vecinos más cercanos
    D, I = vectorstore.index.search(q_emb, k=1)  # D: distancias, I: índices

    # Obtener distancia y categoría más cercana
    distancia_min = D[0][0]
    categoria_idx = I[0][0]

    # Obtener nombre de la categoría desde los metadatos
    categoria_mas_cercana = vectorstore.docstore._dict[list(vectorstore.docstore._dict.keys())[categoria_idx]]
    nombre_categoria = categoria_mas_cercana.metadata["categoria"]

    # Decidir si es relevante o no
    if distancia_min < umbral:
        return nombre_categoria, distancia_min
    else:
        return "no_relevante", distancia_min

def evaluar_pregunta(pregunta_usuario):
    # Clasificar la pregunta
    categoria, distancia = clasificar_con_umbral(pregunta_usuario)

    # Generar el prompt basado en la categoría
    if categoria == "1_poliza_hogar":
        return categoria
    elif categoria == "2_siniestralidad":
        return categoria
    else:
        return categoria