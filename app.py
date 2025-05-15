from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import google.generativeai as genai

# Configurações
debug = config("DEBUG", cast=bool, default=True)
api_key = config("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Inicialização do app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para entrada da API
class ItemList(BaseModel):
    itens: list[str]

# Função auxiliar para montar o prompt
def montar_prompt(itens: list[str]) -> str:
    lista_formatada = ", ".join(itens)
    return f"""
Organize os itens da lista de compras a seguir com base nas seguintes categorias de um mercado: 
Hortifruti, Padaria, Açougue, Frios e Laticínios, Mercearia, Limpeza, Higiene Pessoal, Bebidas, Outros.

- Se algum item não se encaixar claramente em nenhuma das categorias principais, coloque na categoria "Outros".
- Mantenha apenas os nomes dos produtos como valores em cada categoria.
- Responda em formato JSON, com as categorias como chaves e listas de produtos como valores.

Itens a organizar: [{lista_formatada}]
"""

# Rota para organizar os itens
@app.post("/organizar-lista")
async def organizar_lista(data: ItemList):
    try:
        prompt = montar_prompt(data.itens)
        response = model.generate_content(prompt)
        return {"resultado": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

