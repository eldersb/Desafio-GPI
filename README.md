# Desafio-GPI

Desafio Técnico: Extração e Modelagem de Dados de Almoxarifado
**Objetivo:** Desenvolver uma solução para extrair, transformar e carregar dados de um arquivo PDF contendo informações de um almoxarifado, modelando-os em um banco de dados relacional.

## Modelagem do Banco

![image](https://github.com/user-attachments/assets/ee60b44a-ef2f-4a8a-aae6-232cf17bd86b)


Arquivo PDF: https://files.cercomp.ufg.br/weby/up/355/o/Lista_de_estoque_DMP.pdf

* É necessário, para executar o código, ter o Python previamente intalado e um editor de sua preferência(Ex: Vs Code).
* Crie um banco de dados em seu Sistema de Gerenciamento de Banco de Dados(SGBDR) com o seguinte script:

  ```
CREATE DATABASE almoxarifado;
  ```

* O próprio código irá baixar o arquivo PDF e executar os seguintes scripts para criação do banco de dados:

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

*Logo após, serão inseridos no banco os dados que foram coletados do arquivo com os seguintes comandos dentro do arquivo *db_operations*:

```
INSERT INTO grupo (codigo_grupo, nome_grupo) 
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
```

```
INSERT INTO produtos (codigo, denominacao, unidade_medida, grupo_id)
 VALUES (%s, %s, %s, %s)
```
