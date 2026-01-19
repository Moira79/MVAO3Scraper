import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import argparse
from unidecode import unidecode

# Configurações de Resiliência
DELAY = 3  # Segundos entre requisições
RETRIES = 2 # Quantas vezes tentar de novo se der erro 525 ou similar

def get_authors(soup_byline):
    authors = []
    if soup_byline:
        tags = soup_byline.find_all('a')
        for tag in tags:
            authors.append(tag.text)
    return authors

# ... (as outras funções de tags e stats permanecem iguais)
def get_tag_info(category, meta):
    try:
        tag_list = meta.find("dd", class_=str(category) + ' tags').find_all(class_="tag")
    except AttributeError: return []
    return [unidecode(result.text) for result in tag_list] 

def get_stats(meta):
    categories = ['language', 'published', 'status', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits'] 
    stats = list(map(lambda category: meta.find("dd", class_=category), categories))
    if not stats[2]: stats[2] = stats[1]
    try: stats = [unidecode(stat.text) for stat in stats]
    except AttributeError:
        stats = [unidecode(s.text) if s else 'null' for s in stats]
    status = meta.find("dt", class_="status")
    stats.insert(2, status.text.strip(':') if status else 'Completed')
    return stats

def get_tags(meta):
    tags = ['rating', 'category', 'fandom', 'relationship', 'character', 'freeform']
    return list(map(lambda tag: get_tag_info(tag, meta), tags))

def scrape_with_retry(session, fic_id, writer, errorwriter):
    url = f'https://archiveofourown.org/works/{fic_id}?view_adult=true'
    
    for i in range(RETRIES + 1):
        try:
            print(f'Extraindo ID: {fic_id} (Tentativa {i+1})')
            req = session.get(url, timeout=15) # Timeout evita que o script trave
            
            if req.status_code == 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                meta = soup.find("dl", class_="work meta group")
                if meta:
                    author = get_authors(soup.find("h3", class_="byline heading"))
                    tags = get_tags(meta)
                    stats = get_stats(meta)
                    title = unidecode(soup.find("h2", class_="title heading").text).strip()
                    row = [fic_id] + [title] + [author] + list(map(lambda x: ', '.join(x), tags)) + stats + ["", "", ""]
                    writer.writerow(row)
                    print(f'Sucesso no ID {fic_id}!')
                    return True
                else:
                    print(f'Fic restrita ou erro de meta no ID {fic_id}')
                    return False
            
            print(f'Erro {req.status_code} no ID {fic_id}')
            if i < RETRIES: time.sleep(10) # Espera mais tempo antes de tentar de novo

        except Exception as e:
            print(f'Falha de conexão no ID {fic_id}: {e}')
            if i < RETRIES: time.sleep(10)
            
    errorwriter.writerow([fic_id, "Falhou após retentativas"])
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ids')
    args = parser.parse_args()
    
    csv_out = 'fanfics_limpo.csv'
    
    # Criar Sessão para reutilizar a conexão (Resolve o Erro 525)
    session = requests.Session()
    session.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'})
    session.cookies.set('accepted_tos', '20240522', domain='archiveofourown.org')
    session.cookies.set('view_adult', 'true', domain='archiveofourown.org')

    if not os.path.exists(csv_out):
        with open(csv_out, 'w', newline="") as f:
            header = ['work_id', 'title', 'author', 'rating', 'category', 'fandom', 'relationship', 'character', 'tags', 'language', 'published', 'status', 'status_date', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits', 'all_kudos', 'all_bookmarks', 'body']
            csv.writer(f).writerow(header)

    with open(csv_out, 'a', newline="") as f_out, open("errors_get_fics.csv", 'a', newline="") as e_out:
        writer = csv.writer(f_out)
        errorwriter = csv.writer(e_out)
        
        with open(args.ids, 'r') as f_in:
            reader = csv.reader(f_in)
            for row in reader:
                if not row: continue
                scrape_with_retry(session, row[0], writer, errorwriter)
                time.sleep(DELAY)

if __name__ == "__main__":
    main()