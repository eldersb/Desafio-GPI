import pdfplumber
import requests
import os
import pandas as pd  

def download_pdf(url, path_destination):
    """Baixar o PDF da URL e salvar localmente"""
    response = requests.get(url)
    with open(path_destination, 'wb') as f:
        f.write(response.content)

def extract_dados_pdf(pdf_path):
    """Extrair dados do PDF e organizar em um DataFrame"""
    with pdfplumber.open(pdf_path) as pdf:
        # Lista para armazenar os dados de todas as páginas
        all_data = []
        
        # Iterar sobre todas as páginas do PDF
        for page in pdf.pages:
            # Extrair a tabela de cada página
            table = page.extract_table()
            
            if table:
                # Converte a tabela extraída para DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                
                # Remover espaços extras dos nomes das colunas
                df.columns = df.columns.str.strip()
                
                # Adicionar os dados da página à lista
                all_data.append(df)
        
    # Concatenar todos os DataFrames das páginas em um único DataFrame
    df_final = pd.concat(all_data, ignore_index=True)

    # Vamos criar uma coluna extra para o "Código do Grupo"
    group_code = None

    # Iterar sobre as linhas e preencher o código do grupo onde necessário
    for index, row in df_final.iterrows():
        if pd.isna(row['Código']) or row['Código'] == '':
            # Se o código estiver vazio, assumimos que é um item do grupo
            df_final.at[index, 'Código'] = group_code
        else:
            # Se o código não for vazio, é um novo grupo, então atualizamos o código
            group_code = row['Código']

    # Salvar os dados extraídos em um arquivo Excel
    df_final.to_excel("dados_extraidos.xlsx", index=False)

    # Exibir o DataFrame completo (opcional)
    print(df_final)
    
    return df_final

# URL do PDF
url_pdf = "https://files.cercomp.ufg.br/weby/up/355/o/Lista_de_estoque_DMP.pdf"
# Caminho local onde o PDF será salvo
caminho_local_pdf = "Lista_de_estoque_DMP.pdf"

# Baixar o PDF da URL
download_pdf(url_pdf, caminho_local_pdf)

# Extrair os dados do PDF
dados_estoque = extract_dados_pdf(caminho_local_pdf)

# Excluir o arquivo local após o uso
os.remove(caminho_local_pdf)

# Mostrar os dados extraídos (opcional)
print(dados_estoque)
