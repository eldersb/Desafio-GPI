# db_connection.py

import mysql.connector
from mysql.connector import Error

# Conexão ao banco de dados 
def connect_db():
    """Função para estabelecer a conexão com o banco de dados MySQL"""
    try:
        conn = mysql.connector.connect(
            host="localhost",      
            user="root",          
            password="",  
            database="almoxarifado"   
        )
        if conn.is_connected():
            print("Conexão bem-sucedida ao banco de dados!")
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

