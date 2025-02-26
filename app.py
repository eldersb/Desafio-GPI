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
    """Extrair dados do PDF e organizar em um DataFrame corretamente"""
    all_data = []
    column_names = None  # Variável para armazenar os nomes das colunas

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            table = page.extract_table()

            if table:
                # Se ainda não capturamos os nomes das colunas, pegamos da primeira tabela
                if column_names is None:
                    column_names = table[0]  # Primeira linha contém os nomes das colunas
                    table = table[1:]  # Removemos a linha de cabeçalho

                # Criamos o DataFrame
                df = pd.DataFrame(table, columns=column_names)

                # Removemos espaços extras nos nomes das colunas
                df.columns = df.columns.str.strip()

                # Adicionar ao conjunto de dados
                all_data.append(df)

    # Concatenar todos os DataFrames das páginas em um único DataFrame
    final_df = pd.concat(all_data, ignore_index=True)

    # Remover espaços extras dos valores
    final_df = final_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Ajustar os códigos dos grupos corretamente
    for index, row in final_df.iterrows():
        if pd.isna(row["Unid.Medida"]) or row["Unid.Medida"] == "":
            # Linha é um grupo, precisamos pegar os 4 primeiros dígitos do próximo produto
            next_row = final_df.iloc[index + 1] if index + 1 < len(final_df) else None
            if next_row is not None and isinstance(next_row["Código"], str):
                final_df.at[index, "Código"] = next_row["Código"][:4]  # Prefixo do grupo

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

# Função para inserir os dados do DataFrame no banco de dados
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
    
    # Filtrar os registros que são grupos (onde 'Unid.Medida' é None ou NULL)
    grupos_df = df[df['Unid.Medida'].isna() | (df['Unid.Medida'] == '')]
    
    # Filtrar os registros que são produtos (onde 'Unid.Medida' não é None nem vazio)
    produtos_df = df[~df['Unid.Medida'].isna() & (df['Unid.Medida'] != '')]
    
    # Inserir os grupos na tabela grupo
    for index, row in grupos_df.iterrows():
        grupo_codigo = str(row['Código']).strip()  # Aqui deve ser o código do grupo
        grupo_nome = row['Denominação']  # Usando 'Denominação' como o nome do grupo
        
        # Verificar se o código do grupo não é vazio ou None
        if grupo_codigo and grupo_nome:
            # Verificar se o grupo já existe no banco de dados
            cursor.execute("SELECT id FROM grupo WHERE codigo_grupo = %s", (grupo_codigo,))
            grupo_id = cursor.fetchone()
            
            # Se o grupo não existir, insira o grupo na tabela
            if not grupo_id:
                cursor.execute(insert_grupo_query, (grupo_codigo, grupo_nome))
                grupo_id = cursor.lastrowid  # Obter o ID do grupo recém inserido
            else:
                grupo_id = grupo_id[0]  # Caso o grupo já exista, use o ID do grupo
        else:
            print(f"Grupo com código '{grupo_codigo}' ou nome '{grupo_nome}' inválido. Não inserido.")
    
    # Agora inserimos os produtos associando-os aos grupos:
    for index, row in produtos_df.iterrows():
        produto_codigo = str(row['Código']).strip()  # Código do produto
        produto_denominacao = row['Denominação']
        produto_unidade = row['Unid.Medida']
        
        # Extrair os 4 primeiros dígitos do código do produto para determinar o grupo
        grupo_codigo = produto_codigo[:4].strip()  # Pega os 4 primeiros dígitos do código do produto, sem espaços
        
        # Verificar se o grupo existe no banco de dados
        cursor.execute("SELECT id FROM grupo WHERE codigo_grupo = %s", (grupo_codigo,))
        grupo_id = cursor.fetchone()
        
        # Se o grupo não existir, não inserimos o produto
        if grupo_id:
            grupo_id = grupo_id[0]  # Recupera o ID do grupo correspondente
            # Inserir o produto na tabela
            dados_produto = (produto_codigo, produto_denominacao, produto_unidade, grupo_id)
            cursor.execute(insert_produto_query, dados_produto)
        else:
            print(f"Grupo {grupo_codigo} não encontrado para o produto {produto_codigo}. Produto não inserido.")
    
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
