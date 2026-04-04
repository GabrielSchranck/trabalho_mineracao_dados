# 🏀 NBA Web Scraping & Data Mining

Este projeto foi desenvolvido no contexto da disciplina de **Mineração de Dados**, com o objetivo de realizar a **coleta, tratamento e análise exploratória de dados** a partir da loja oficial da NBA.

A base construída será utilizada nas próximas etapas da disciplina para aplicação de técnicas de **mineração de dados e construção de dashboards**.

---

## 📌 Objetivo

* Coletar dados de produtos via **web scraping**
* Estruturar os dados em formato tabular
* Aplicar um pipeline de **ETL (Extract, Transform, Load)**
* Realizar limpeza e pré-processamento
* Preparar a base para análises futuras

---

## 🧰 Tecnologias Utilizadas

* Python 3
* BeautifulSoup
* Requests
* Pandas
* Regex (re)
* JSON
* Loguru

---

## 📊 Fonte de Dados

Os dados foram coletados da loja oficial da NBA:

🔗 https://www.lojanba.com/

* Mais de **3.100 registros coletados**
* Dados distribuídos em **42 categorias**
* Produtos como camisetas, tênis, regatas, bonés, etc.

---

## ⚙️ Pipeline ETL

O projeto segue um fluxo completo de ETL:

```
Extração (Scraping)
        ↓
Parsing HTML / JSON
        ↓
Estruturação (DataFrame)
        ↓
Análise inicial dos dados
        ↓
Limpeza e transformação
        ↓
Base final (CSV)
```

### 📌 Explicação das etapas:

### 1. Extração (Extract)

* Coleta de dados via HTTP (Requests)
* Extração de categorias via JSON (`__INITIAL_STATE__`)
* Navegação por paginação (`&page`)

### 2. Transformação (Transform)

* Limpeza de texto
* Remoção de duplicatas (SKU)
* Conversão de valores numéricos
* Tratamento de valores ausentes
* Remoção de colunas esparsas
* Detecção de outliers (IQR)
* Normalização de dados (Min-Max)
* Criação de faixa de preço

### 3. Carga (Load)

* Exportação para CSV (`products.csv`)
* Dados estruturados prontos para análise

---

## 🚀 Como Executar

### 1. Clonar o projeto

```bash
git clone https://github.com/seu-repo/nba-scraping.git
cd nba-scraping
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar scraping

```bash
python main.py
```

---

## 📈 Resultados

* 📦 Registros brutos: **3.118**
* 🧹 Após limpeza: **756**
* 🔁 Duplicatas removidas: **2.362**
* ⚠️ Outliers identificados: **67**

---

## 🧠 Principais Desafios

* Extração de dados carregados via JavaScript
* Tratamento de grande volume de duplicatas
* Presença de colunas com mais de 90% de valores nulos
* Padronização de dados heterogêneos

---

## 🔮 Próximos Passos

* Análise exploratória avançada
* Modelos de Machine Learning
* Clusterização de produtos
* Construção de dashboard interativo

---

## 📚 Referências

* BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
* Requests: https://docs.python-requests.org/
* Pandas: https://pandas.pydata.org/

---

## 👨‍💻 Autores

* Pedro Rufino da Mata Neto
* Gabriel Cardoso Schranck

---
