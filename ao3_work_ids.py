from bs4 import BeautifulSoup
import re
import time
import requests
import csv
import sys
import datetime
import argparse
import os

page_empty = False
base_url = ""
url = ""
num_requested_fic = 0
num_recorded_fic = 0
csv_name = ""
multichap_only = ""
tags = []
seen_ids = set()

def get_args():
    global base_url, url, csv_name, num_requested_fic, multichap_only, tags
    parser = argparse.ArgumentParser(description='Scrape AO3 work IDs given a search URL')
    parser.add_argument('url', metavar='URL', help='a single URL pointing to an AO3 search page')
    parser.add_argument('--out_csv', default='work_ids', help='csv output file name')
    parser.add_argument('--header', default='', help='user http header')
    parser.add_argument('--num_to_retrieve', default='a', help='how many fic ids you want')
    parser.add_argument('--multichapter_only', default='', help='only retrieve ids for multichapter fics')
    parser.add_argument('--tag_csv', default='', help='optional list of tags')

    args = parser.parse_args()
    url = args.url
    csv_name = str(args.out_csv)
    num_requested_fic = -1 if str(args.num_to_retrieve) == 'a' else int(args.num_to_retrieve)
    multichap_only = bool(args.multichapter_only)
    return args.header

def get_ids(header_info=''):
    global page_empty, seen_ids
    
    # 1. Identidade de Navegador (User-Agent) - Essencial para não ser bloqueado
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 2. Cookies atualizados para os Termos de Serviço de 2024
    cookies = {
        'accepted_tos': '20240522', 
        'view_adult': 'true'
    }
    
    req = requests.get(url, headers=headers, cookies=cookies)
    
    while req.status_code == 429:
        print("\nO AO3 pediu para esperar (Erro 429). Aguardando 30 segundos...")
        time.sleep(30)
        req = requests.get(url, headers=headers, cookies=cookies)

    soup = BeautifulSoup(req.text, "lxml")
    
    # DIAGNÓSTICO: Isso vai imprimir no seu terminal o título da página que o script capturou
    page_title = soup.title.text.strip() if soup.title else "Sem título"
    print(f"\n[DEBUG] Acessando: {page_title}")

    works = soup.select("li.work.blurb.group")
    if (len(works) == 0):
        page_empty = True
        print("[AVISO] Nenhuma história encontrada nesta página.")

    ids = []
    for tag in works:
        t = tag.get('id')[5:] # Remove 'work_' do ID
        if not t in seen_ids:
            ids.append(t)
            seen_ids.add(t)
    return ids

# --- Funções de suporte (mantidas do original para funcionamento) ---
def update_url_to_next_page():
    global url
    key = "page="
    start = url.find(key)
    if (start != -1):
        page_start_index = start + len(key)
        page_end_index = url.find("&", page_start_index)
        if (page_end_index != -1):
            page = int(url[page_start_index:page_end_index]) + 1
            url = url[:page_start_index] + str(page) + url[page_end_index:]
        else:
            page = int(url[page_start_index:]) + 1
            url = url[:page_start_index] + str(page)
    else:
        url = url + ("&page=2" if "?" in url else "?page=2")

def write_ids_to_csv(ids):
    global num_recorded_fic
    with open(csv_name + ".csv", 'a', newline="") as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        for id in ids:
            if (num_recorded_fic < num_requested_fic or num_requested_fic == -1):
                wr.writerow([id, url])
                num_recorded_fic += 1
            else: break

def main():
    get_args()
    print("Iniciando coleta...")
    if os.path.exists(csv_name + ".csv"):
        print("Lendo IDs já existentes para evitar duplicatas...")
        with open(csv_name + ".csv", 'r') as f:
            reader = csv.reader(f)
            for row in reader: seen_ids.add(row[0])
    
    while not page_empty and (num_recorded_fic < num_requested_fic or num_requested_fic == -1):
        time.sleep(5) # Respeita o servidor
        ids = get_ids()
        if ids:
            write_ids_to_csv(ids)
            print(f"Coletados {len(ids)} IDs nesta página. Total: {num_recorded_fic}")
        update_url_to_next_page()
    
    print("\nProcesso finalizado. Verifique seu arquivo CSV.")

if __name__ == "__main__":
    main()