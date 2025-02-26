
# Função para criar a tabela no banco de dados (caso não exista)
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


    # Função para inserir os dados do DataFrame no banco de dados
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
        grupos_df = df[df['Unid.Medida'].isna() | (df['Unid.Medida'] == '')]
        
        # Filtrar os registros que são produtos (onde 'Unid.Medida' não é None nem vazio)
        produtos_df = df[~df['Unid.Medida'].isna() & (df['Unid.Medida'] != '')]
        
        # Inserir os grupos na tabela grupo
        for index, row in grupos_df.iterrows():
            grupo_codigo = str(row['Código']).strip()  # Código do grupo
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
        print("Dados inseridos com sucesso!")

    except Error as e:
        print(f"Erro ao inserir dados: {e}")