
from getpass import getpass

from main import engine
from sqlalchemy import text
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

print("=== CADASTRO DO ADMINISTRADOR ===")

nome = input("Nome completo: ")
email = input("E-mail: ")
login = input("Login: ")
senha = getpass("Senha: ")
confirmacao = getpass("Confirme a senha: ")

if not all([nome, email, login, senha]):
    print("Preencha todos os campos.")
    raise SystemExit

if senha != confirmacao:
    print("As senhas não coincidem.")
    raise SystemExit

senha_criptografada = password_hash.hash(senha)

try:
    with engine.begin() as conexao:
        conexao.execute(
            text("""
                INSERT INTO usuarios
                (nome, email, login, senha, tipo, status)
                VALUES
                (:nome, :email, :login, :senha, 'administrador', 'ativo')
            """),
            {
                "nome": nome,
                "email": email,
                "login": login,
                "senha": senha_criptografada
            }
        )

    print("Administrador cadastrado com sucesso!")

except Exception as erro:
    print("Não foi possível cadastrar:", erro)
