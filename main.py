from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import bcrypt
from database import criar_tabelas
print("Importando o modelo Idealizador de models")
from models import Idealizador
print("Modelo Idealizador importado com sucesso!")
from pydantic import BaseModel

# 🔹 APP
app = FastAPI(title="Cadastro de Idealizadores")

# 🔹 Permitir acesso do front-end (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Cria tabelas se não existirem
criar_tabelas()

@app.get("/")
def home():
    return {"mensagem": "API de Cadastro funcionando 🚀"}

# ===================== CADASTRO =====================
@app.post("/cadastro")
def cadastrar(idealizador: Idealizador):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    senha_criptografada = bcrypt.hashpw(idealizador.senha.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO idealizadores (nome, telefone, email, senha, github, linkedin, funcao, pais, cidade, sobre_mim)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            idealizador.nome,
            idealizador.telefone,
            idealizador.email,
            senha_criptografada,
            idealizador.github,
            idealizador.linkedin,
            idealizador.funcao,
            idealizador.pais,
            idealizador.cidade,
            idealizador.sobre_mim
        ))
        conexao.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    finally:
        conexao.close()

    return {"mensagem": "Idealizador cadastrado com sucesso!"}


# ===================== LOGIN =====================
class Login(BaseModel):
    email: str
    senha: str

@app.post("/login")
def login(credenciais: dict):
    email = credenciais.get("email")
    senha = credenciais.get("senha")

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT senha, nome FROM idealizadores WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    conexao.close()

    if not resultado:
        return {"mensagem": "Usuário não encontrado"}

    senha_armazenada, nome = resultado
    if bcrypt.checkpw(senha.encode('utf-8'), senha_armazenada):
        return {"mensagem": f"Bem-vindo {nome}!"}
    else:
        return {"mensagem": "Senha incorreta"}

