
# Criação da tabela no banco de dados (caso não exista)
def create_table(conn):
    
    try:
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
        print("Tabelas craidas com sucesso!")

    except Error as e:
        print(f"Erro ao criar tabelas: {e}")


# Inserir os dados do DataFrame no banco de dados
def insert_data(conn, df):
    """Inserir os dados do DataFrame no banco de dados"""
    try:
        cursor = conn.cursor()
        
        insert_grupo_query = """
        INSERT INTO grupo (codigo_grupo, nome_grupo) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
        """
        
        insert_produto_query = """
        INSERT INTO produtos (codigo, denominacao, unidade_medida, grupo_id)
        VALUES (%s, %s, %s, %s)
        """
        
        # Filtrar os registros que são grupos (onde 'Unid.Medida' é None ou NULL)
        grupos_dataframe = df[df['Unid.Medida'].isna() | (df['Unid.Medida'] == '')]
        
        # Filtrar os registros que são produtos (onde 'Unid.Medida' não é None nem null)
        produtos_df = df[~df['Unid.Medida'].isna() & (df['Unid.Medida'] != '')]
        
        # Inserir os grupos na tabela grupo
        for index, row in grupos_dataframe.iterrows():
            grupo_codigo = str(row['Código']).strip()  # Código do grupo
            grupo_nome = row['Denominação']  # Usando 'Denominação' como o nome do grupo
            
            # Verifica se o código do grupo não é vazio ou None
            if grupo_codigo and grupo_nome:

                cursor.execute("SELECT id FROM grupo WHERE codigo_grupo = %s", (grupo_codigo,))
                grupo_id = cursor.fetchone()
                
               
                if not grupo_id:
                    cursor.execute(insert_grupo_query, (grupo_codigo, grupo_nome))
                    grupo_id = cursor.lastrowid  
                else:
                    grupo_id = grupo_id[0]  
            else:
                print(f"Grupo com código '{grupo_codigo}' ou nome '{grupo_nome}' inválido. Não inserido.")
        
        # Insere os produtos associando-os aos grupos:
        for index, row in produtos_df.iterrows():
            produto_codigo = str(row['Código']).strip()  
            produto_denominacao = row['Denominação']
            produto_unidade = row['Unid.Medida']
            
            grupo_codigo = produto_codigo[:4].strip()  
            
            cursor.execute("SELECT id FROM grupo WHERE codigo_grupo = %s", (grupo_codigo,))
            grupo_id = cursor.fetchone()
            

            if grupo_id:
                grupo_id = grupo_id[0]  

                dados_produto = (produto_codigo, produto_denominacao, produto_unidade, grupo_id)
                cursor.execute(insert_produto_query, dados_produto)
            else:
                print(f"Grupo {grupo_codigo} não encontrado para o produto {produto_codigo}. Produto não inserido.")
        
       
        conn.commit()
        print("Dados inseridos com sucesso!")

    except Error as e:
        print(f"Erro ao inserir dados: {e}")