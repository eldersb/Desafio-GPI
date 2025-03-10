# Desafio-GPI

Desafio Técnico: Extração e Modelagem de Dados de Almoxarifado

**Objetivo:** Desenvolver uma solução para extrair, transformar e carregar dados de um arquivo PDF contendo informações de um almoxarifado, modelando-os em um banco de dados relacional.

## Ferramentas
* Python 3.13
* MySQL

## Modelagem do Banco

![image](https://github.com/user-attachments/assets/41981e10-d80c-4619-bca1-68f880c6e405)


## Passo a Passo de Execução do Projeto

**Arquivo PDF:** https://files.cercomp.ufg.br/weby/up/355/o/Lista_de_estoque_DMP.pdf

* É necessário, para executar o código, ter o Python previamente instalado, um SGRBD e um editor de sua preferência (Ex: Vs Code).

> [!NOTE]  
> Link de instalação Python - https://www.python.org/downloads/

* Crie um banco de dados em seu Sistema de Gerenciamento de Banco de Dados(SGBDR) com o seguinte script:

  ```
  CREATE DATABASE almoxarifado;
  ```

* Verifique dentro do arquivo db_connection.py a conexão:

  ```
  conn = mysql.connector.connect(
            host="localhost",      
            user="root",          
            password="",  -> Caso tenha senha insira.
            database="almoxarifado"   
        )
  ```

* O próprio código irá baixar o arquivo PDF e executar os scripts para criação do banco de dados, basta rodar o comando **python appy.py** no terminal.
* Os comandos de criação de banco de dados estão no arquivo **db_operations.py**:

```
 CREATE TABLE IF NOT EXISTS grupo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_grupo VARCHAR(50) UNIQUE,
            nome_grupo VARCHAR(255)
        )

```

```
 CREATE TABLE IF NOT EXISTS produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(50),
            denominacao TEXT,
            unidade_medida VARCHAR(50),
            grupo_id INT,
            FOREIGN KEY (grupo_id) REFERENCES grupo(id)
        )

```

*Logo após, serão inseridos no banco os dados que foram coletados do arquivo com os seguintes comandos dentro do arquivo **db_operations**:

```
INSERT INTO grupo (codigo_grupo, nome_grupo) 
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
```

```
INSERT INTO produtos (codigo, denominacao, unidade_medida, grupo_id)
 VALUES (%s, %s, %s, %s)
```

* Caso queira avaliar como os dados estão sendo extraídos, dentro do app.py execute o comando:

  ```
  print(data_stock)
  ```

* Após a execução, confira no banco de dados a criação e inserção dos registros na tabela:

### Tabela GRUPO
  ![image](https://github.com/user-attachments/assets/422d8ba2-7f86-4777-8162-ffe9a5c6b789)

### Tabela PRODUTOS
  ![image](https://github.com/user-attachments/assets/b9f7ad27-ff53-4b5b-a36f-c5999717d444)

