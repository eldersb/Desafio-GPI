import pdfplumber
import requests
import pandas as pd

# Função para baixar o PDF
def download_pdf(url, path_destination):
    """Baixar o PDF da URL e salvar localmente"""
    try:
        response = requests.get(url)

        with open(path_destination, 'wb') as f:
            f.write(response.content)
        
        print("PDF baixado com sucesso!")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o PDF: {e}")


# Função para extrair os dados do PDF
def extract_dados_pdf(pdf_path):
    """Extrair dados do PDF e organizar em um DataFrame corretamente"""
    try:
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
        final_df = final_df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

        # Ajustar os códigos dos grupos corretamente
        for index, row in final_df.iterrows():
            if pd.isna(row["Unid.Medida"]) or row["Unid.Medida"] == "":
                # Linha é um grupo, precisamos pegar os 4 primeiros dígitos do próximo produto
                next_row = final_df.iloc[index + 1] if index + 1 < len(final_df) else None
                if next_row is not None and isinstance(next_row["Código"], str):
                    final_df.at[index, "Código"] = next_row["Código"][:4]  # Prefixo do grupo

        print("Dados extraídos do PDF com sucesso!")
        return final_df
    
    except Exception as e:
        print(f"Erro ao extrair dados do PDF: {e}")
        return pd.DataFrame() 