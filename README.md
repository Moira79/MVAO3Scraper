# AO3 Scraper - Moira's Version

Este repositório é um fork do projeto original `radiolarian/AO3Scraper`, atualizado e otimizado para a coleta e análise estatística de fanfictions do Archive of Our Own (AO3).

## 🚀 Melhorias Implementadas

Diferente da versão original, esta versão inclui:

* **Bypass de Termos de Serviço (TOS):** Implementação de cookies automáticos para ignorar a barreira de aceitação de termos e avisos de conteúdo adulto do AO3.
* **Extração Otimizada de Metadados:** Modificação do script de coleta para extrair apenas dados estatísticos (Kudos, Hits, Tags, etc.), ignorando o corpo do texto para acelerar o processo em até 10x.
* **Resiliência de Conexão:** Uso de `requests.Session()` e lógica de re-tentativas para evitar erros de SSL (525) e bloqueios do Cloudflare.

## 🛠️ Tecnologias Utilizadas

* **Python 3.12**
* **Pandas:** Para manipulação e análise de dados.
* **BeautifulSoup4:** Para web scraping e parsing de HTML.
* **Requests:** Para comunicação com a API/Web do AO3.