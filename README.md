# MVAO3Scraper - Coletor de Dados do AO3

Este projeto é uma ferramenta de *web scraping* desenvolvida em Python para extrair metadados de fanfics do site **Archive of Our Own (AO3)**. 

O foco é a **análise de dados** (Data Analytics), coletando informações estatísticas e categorizadas (Ships, Personagens, Ratings, Kudos, etc.) diretamente das páginas de listagem, otimizando o tempo de coleta e respeitando os limites do servidor.

## 🚀 Funcionalidades

* **Coleta Otimizada:** Extrai todos os dados diretamente da lista de busca (não precisa entrar em cada história individualmente).
* **Dados Estruturados:** Separa automaticamente Tags de Aviso, Ships, Personagens e Tags Extras em colunas distintas.
* **Resiliência:** Sistema automático de retentativa para erros de conexão (525/502) e pausas inteligentes para limites de requisição (Erro 429).
* **Saída em CSV:** Gera planilhas prontas para análise em Pandas, Excel ou Power BI.

## 📋 Pré-requisitos

* Python 3.10+
* Ambiente Linux (Recomendado) ou Windows

## 🛠️ Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Moira79/MVAO3Scraper.git](https://github.com/Moira79/MVAO3Scraper.git)
    cd MVAO3Scraper
    ```

2.  **Crie e ative o ambiente virtual (Linux):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install requests beautifulsoup4 lxml pandas unidecode
    # Ou se tiver o arquivo requirements:
    pip install -r requirements.txt
    ```