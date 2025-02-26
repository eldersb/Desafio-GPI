# db_connection.py

import mysql.connector
from mysql.connector import Error

def criar_conexao():
    """Função para estabelecer uma conexão com o banco de dados MySQL."""
    try:
        conn = mysql.connector.connect(
            host="localhost",      # Endereço do servidor
            user="root",           # Nome de usuário
            password="",  # Senha do usuário
            database="almoxarifado"   # Nome do banco de dados
        )
        
        if conn.is_connected():
            print("Conexão bem-sucedida ao banco de dados!")
            return conn  # Retorna a conexão
        else:
            print("Falha na conexão com o banco de dados.")
            return None

    except Error as e:
        print(f"Erro de conexão: {e}")
        return None

def fechar_conexao(conn):
    """Função para fechar a conexão com o banco de dados."""
    if conn and conn.is_connected():
        conn.close()
        print("Conexão fechada.")

criar_conexao()