
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ==========================================
# CONFIGURAÇÕES
# ==========================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "eletroniza")

# ==========================================
# CONEXÃO COM MYSQL
# ==========================================

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# ==========================================
# APLICAÇÃO FASTAPI
# ==========================================

app = FastAPI(
    title="EletroNiza API",
    description="Sistema de gerenciamento de armários e ferramentas",
    version="1.0.0"
)

# CORS para desenvolvimento local.
# Em produção, limitar às origens autorizadas.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

password_hash = PasswordHash.recommended()

# ==========================================
# MODELO DE LOGIN
# ==========================================

class LoginRequest(BaseModel):
    usuario: str
    senha: str


# ==========================================
# ROTA INICIAL
# ==========================================

@app.get("/")
def inicio():
    return {
        "mensagem": "API do EletroNiza funcionando!"
    }


# ==========================================
# TESTAR CONEXÃO COM MYSQL
# ==========================================

@app.get("/teste-banco")
def testar_banco():
    try:
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))

        return {
            "status": "conectado",
            "banco": DB_NAME
        }

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na conexão com o banco: {str(erro)}"
        )


# ==========================================
# LOGIN
# ==========================================

@app.post("/login")
def fazer_login(dados: LoginRequest):

    # Procurar usuário no banco
    with engine.connect() as conexao:
        usuario = conexao.execute(
            text("""
                SELECT
                    id,
                    nome,
                    email,
                    login,
                    senha,
                    tipo,
                    status
                FROM usuarios
                WHERE login = :login
            """),
            {
                "login": dados.usuario
            }
        ).mappings().first()

    # Verificar se o usuário existe
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos."
        )

    # Verificar se está ativo
    if usuario["status"] != "ativo":
        raise HTTPException(
            status_code=403,
            detail="Este usuário está bloqueado."
        )

    # Verificar senha
    try:
        senha_correta = password_hash.verify(
            dados.senha,
            usuario["senha"]
        )
    except Exception:
        senha_correta = False

    if not senha_correta:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos."
        )

    # Login realizado
    return {
        "mensagem": "Login realizado com sucesso!",
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "login": usuario["login"],
        "tipo": usuario["tipo"]
    }
