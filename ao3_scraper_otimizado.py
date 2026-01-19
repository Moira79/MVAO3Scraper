import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse
import sys
import os

# --- Configurações Globais ---
# Cabeçalhos para fingir ser um navegador (evita bloqueio 403)
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# Cookies para aceitar os termos de serviço (evita redirecionamentos)
COOKIES = {
    'accepted_tos': '20240522', 
    'view_adult': 'true'
}

def get_args():
    parser = argparse.ArgumentParser(description='Scraper Otimizado AO3 - Metadados da Lista')
    parser.add_argument('url', help='URL da página de busca/filtro do AO3')
    parser.add_argument('--out_csv', default='dados_ao3', help='Nome do arquivo de saída (sem .csv)')
    parser.add_argument('--pages', default=5, type=int, help='Quantas páginas raspar (padrão: 5)')
    return parser.parse_args()

def extrair_metadados_da_pagina(soup):
    """
    Lê o HTML da página e extrai os dados de cada cartão de história (blurb).
    """
    works_list = []
    
    # Seleciona todos os blocos de história (excluindo marcadores de série ou usuário)
    work_blurbs = soup.select("li.work.blurb.group")
    
    for work in work_blurbs:
        try:
            # 1. ID
            work_id = work.get('id').replace('work_', '')
            
            # 2. Título
            titulo_tag = work.select_one("h4.heading > a")
            titulo = titulo_tag.text.strip() if titulo_tag else "Sem Título"
            
            # 3. Autor (Lida com 'Anonymous')
            autor_tag = work.select_one("a[rel='author']")
            autor = autor_tag.text.strip() if autor_tag else "Anonymous"
            
            # 4. Fandom
            fandoms = [a.text.strip() for a in work.select("h5.fandoms a")]
            fandom_str = ", ".join(fandoms)
            
            # 5. Rating (G/T/M/E) - Pega do ícone de Required Tags
            # O primeiro item da lista de required-tags é o Rating
            rating_tag = work.select_one("ul.required-tags li:nth-of-type(1) span.text")
            rating = rating_tag.text.strip() if rating_tag else "Unknown"

            # 6. Tags: Separando por categoria para colunas organizadas
            # O AO3 coloca classes nas tags: .warnings, .relationships, .characters, .freeforms
            avisos = [t.text.strip() for t in work.select("ul.tags li.warnings a")]
            ships = [t.text.strip() for t in work.select("ul.tags li.relationships a")]
            personagens = [t.text.strip() for t in work.select("ul.tags li.characters a")]
            tags_extras = [t.text.strip() for t in work.select("ul.tags li.freeforms a")]
            
            # 7. Estatísticas (dl.stats)
            stats = work.select_one("dl.stats")
            
            def get_stat(css_class):
                """Função auxiliar para pegar número ou retornar 0 se não existir"""
                tag = stats.select_one(f"dd.{css_class}")
                return tag.text.strip().replace(",", "") if tag else "0"

            palavras = get_stat("words")
            capitulos = get_stat("chapters")
            kudos = get_stat("kudos")
            comentarios = get_stat("comments")
            bookmarks = get_stat("bookmarks")
            hits = get_stat("hits")
            
            # 8. Data de Atualização
            data_tag = work.select_one("p.datetime")
            data_atualizacao = data_tag.text.strip() if data_tag else ""

            # Monta o dicionário da linha
            works_list.append({
                'ID': work_id,
                'Título': titulo,
                'Autor': autor,
                'Fandom': fandom_str,
                'Rating': rating,
                'Avisos': ", ".join(avisos),
                'Ships': ", ".join(ships),
                'Personagens': ", ".join(personagens),
                'Tags Extras': ", ".join(tags_extras),
                'Palavras': palavras,
                'Capítulos': capitulos,
                'Kudos': kudos,
                'Comentários': comentarios,
                'Bookmarks': bookmarks,
                'Hits': hits,
                'Data Atualização': data_atualizacao
            })
            
        except Exception as e:
            print(f"[ERRO] Falha ao processar um item: {e}")
            continue
            
    return works_list

def update_url_page(url, current_page):
    """Atualiza o número da página na URL"""
    if "page=" in url:
        return url.replace(f"page={current_page}", f"page={current_page+1}")
    else:
        # Se não tem 'page=', adiciona no final. Verifica se usa ? ou &
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}page={current_page+1}"

def main():
    args = get_args()
    base_url = args.url
    filename = f"{args.out_csv}.csv"
    max_pages = args.pages
    
    # Colunas do CSV
    fieldnames = ['ID', 'Título', 'Autor', 'Fandom', 'Rating', 'Avisos', 'Ships', 
                  'Personagens', 'Tags Extras', 'Palavras', 'Capítulos', 'Kudos', 
                  'Comentários', 'Bookmarks', 'Hits', 'Data Atualização']

    # Abrir CSV e escrever cabeçalho (se for novo)
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
    
    current_page = 1
    current_url = base_url
    
    print(f"--- Iniciando Coleta: {max_pages} páginas ---")
    print(f"Arquivo de saída: {filename}")

    while current_page <= max_pages:
        print(f"\n[Página {current_page}] Acessando URL...")
        
        try:
            req = requests.get(current_url, headers=HEADERS, cookies=COOKIES)
            
            # Tratamento do erro 429 (Muitas requisições)
            if req.status_code == 429:
                print("⚠️ AO3 pediu pausa (Erro 429). Esperando 60 segundos...")
                time.sleep(60)
                continue # Tenta a mesma página de novo
            
            if req.status_code != 200:
                print(f"Erro ao acessar página: {req.status_code}")
                break

            soup = BeautifulSoup(req.text, "lxml")
            
            # Extração
            dados = extrair_metadados_da_pagina(soup)
            
            if not dados:
                print("Nenhuma história encontrada ou fim da lista.")
                break
                
            # Salvar no CSV imediatamente
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerows(dados)
            
            print(f"✅ Sucesso: {len(dados)} histórias salvas.")
            
            # Preparar próxima página
            current_url = update_url_page(current_url, current_page)
            current_page += 1
            
            # Pausa educada para não ser bloqueado (Essencial!)
            time.sleep(5) 
            
        except KeyboardInterrupt:
            print("\nParando o script a pedido do usuário.")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")
            break

    print("\n--- Coleta Finalizada ---")

if __name__ == "__main__":
    main()