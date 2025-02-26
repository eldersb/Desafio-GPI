import mysql.connector
from mysql.connector import Error
import pdfplumber
import requests
import os
import pandas as pd

# Função para baixar o PDF
def download_pdf(url, path_destination):
    """Baixar o PDF da URL e salvar localmente"""
    response = requests.get(url)
    with open(path_destination, 'wb') as f:
        f.write(response.content)

# Função para extrair os dados do PDF
def extract_dados_pdf(pdf_path):
    """Extrair dados do PDF e organizar em um DataFrame"""
    all_data = []
    column_names = None  # Variável para armazenar os nomes das colunas

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            table = page.extract_table()

            if table:
                # Se os nomes das colunas ainda não foram capturados, capturamos da primeira página
                if column_names is None:
                    column_names = table[0]  # Primeira linha será a coluna
                    table = table[1:]  # Remover a linha de cabeçalho da primeira página
                else:
                    # Remover a linha de cabeçalho das páginas subsequentes
                    table = table

                # Converte a tabela extraída para DataFrame
                df = pd.DataFrame(table, columns=column_names)
                
                # Remover espaços extras dos nomes das colunas
                df.columns = df.columns.str.strip()

                # Vamos criar uma coluna extra para o "Código do Grupo"
                group_code = None

                # Iterar sobre as linhas e preencher o código do grupo onde necessário
                for index, row in df.iterrows():
                    if pd.isna(row['Código']) or row['Código'] == '':
                        df.at[index, 'Código'] = group_code
                    else:
                        group_code = row['Código']

                # Adicionar os dados da página atual à lista de todos os dados
                all_data.append(df)

    # Concatenar todos os DataFrames das páginas em um único DataFrame
    final_df = pd.concat(all_data, ignore_index=True)
    
    return final_df

# Função para conectar ao banco de dados MySQL
def conectar_banco():
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

# Função para criar a tabela no banco de dados (caso não exista)
def criar_tabela(conn):
    """Criar a tabela no banco de dados (caso não exista)"""
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grupo (
        id INT AUTO_INCREMENT PRIMARY KEY,
        codigo_grupo VARCHAR(50) UNIQUE,
        nome_grupo VARCHAR(255)
    )
    """)
    
    # Criar a tabela 'produtos' (associada ao 'grupo')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        codigo VARCHAR(50),
        denominacao TEXT,
        unidade_medida VARCHAR(50),
        grupo_id INT,
        FOREIGN KEY (grupo_id) REFERENCES grupo(id)
    )
    """)

    conn.commit()

def inserir_dados(conn, df):
    """Inserir os dados do DataFrame no banco de dados"""
    cursor = conn.cursor()
    
    # Preparar a query para inserir na tabela 'grupo' (caso o grupo não exista)
    insert_grupo_query = """
    INSERT INTO grupo (codigo_grupo, nome_grupo) 
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
    """
    
    # Preparar a query de inserção para produtos
    insert_produto_query = """
    INSERT INTO produtos (codigo, denominacao, unidade_medida, grupo_id)
    VALUES (%s, %s, %s, %s)
    """
    
    # Iterar pelas linhas do DataFrame
    for index, row in df.iterrows():
        # Inserir o grupo (se não existir) e pegar o id do grupo
        grupo_codigo = row['Código']
        grupo_nome = f"Grupo {grupo_codigo}"  # Pode ajustar conforme o formato do nome do grupo
        
        cursor.execute(insert_grupo_query, (grupo_codigo, grupo_nome))
        grupo_id = cursor.lastrowid  # Pega o ID do grupo recém inserido ou existente
        
        # Inserir o produto
        dados_produto = (row['Código'], row['Denominação'], row['Unid.Medida'], grupo_id)
        cursor.execute(insert_produto_query, dados_produto)
    
    # Commit para salvar as alterações no banco
    conn.commit()

# URL do PDF
url_pdf = "https://files.cercomp.ufg.br/weby/up/355/o/Lista_de_estoque_DMP.pdf"
# Caminho local onde o PDF será salvo
caminho_local_pdf = "Lista_de_estoque_DMP.pdf"

# Baixar o PDF da URL
download_pdf(url_pdf, caminho_local_pdf)

# Extrair os dados do PDF
dados_estoque = extract_dados_pdf(caminho_local_pdf)

# Conectar ao banco de dados
conn = conectar_banco()

if conn:
    # Criar a tabela no banco de dados (se não existir)
    criar_tabela(conn)
    
    # Inserir os dados extraídos no banco de dados
    inserir_dados(conn, dados_estoque)

    # Fechar a conexão após o uso
    conn.close()

# Excluir o arquivo local após o uso
os.remove(caminho_local_pdf)

# Mostrar os dados extraídos (opcional)
print(dados_estoque)
