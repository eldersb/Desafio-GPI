import os
from db_connection import connect_db  # Importando a conexão do novo arquivo
from db_operations import create_table, insert_data
from pdf_extraction import download_pdf, extract_dados_pdf

# URL e caminho do PDF 
url_pdf = "https://files.cercomp.ufg.br/weby/up/355/o/Lista_de_estoque_DMP.pdf"
localpath_pdf = "Lista_de_estoque_DMP.pdf"

# Baixar o PDF da URL
download_pdf(url_pdf, localpath_pdf)

# Extrair os dados do PDF
data_stock = extract_dados_pdf(localpath_pdf)

# Conectar ao banco de dados
conn = connect_db()

if conn:
    # Criar a tabela no banco de dados (se não existir)
    create_table(conn)
    
    # Inserir os dados extraídos no banco de dados
    insert_data(conn, data_stock )

    # Fechar a conexão após o uso
    conn.close()

# Excluir o arquivo local após o uso
os.remove(localpath_pdf)

# Mostrar os dados extraídos do PDF como está no dataframe (opcional)
# print(data_stock)
