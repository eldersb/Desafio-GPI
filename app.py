import os
from db_connection import connect_db  
from db_operations import create_table, insert_data
from pdf_extraction import download_pdf, extract_dados_pdf

url_pdf = "https://files.cercomp.ufg.br/weby/up/355/o/Lista_de_estoque_DMP.pdf"
localpath_pdf = "Lista_de_estoque_DMP.pdf"

download_pdf(url_pdf, localpath_pdf)

data_stock = extract_dados_pdf(localpath_pdf)

conn = connect_db()

if conn:
    create_table(conn)
    
    insert_data(conn, data_stock )

    conn.close()

# Excluir o arquivo local após o uso
os.remove(localpath_pdf)

# Mostrar os dados extraídos do PDF no console (opcional)
# print(data_stock)
