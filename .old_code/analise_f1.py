import pandas as pd

def analisar_dados():
    print("Carregando e limpando os dados...")
    df = pd.read_csv('fanfics_limpo.csv')

    # 1. LIMPEZA DE DADOS (Data Cleaning)
    # Vamos remover as vírgulas e transformar em número real
    colunas_numericas = ['kudos', 'hits', 'words', 'comments']
    
    for col in colunas_numericas:
        # Transforma tudo em texto, remove a vírgula e converte para número
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    # 2. CÁLCULO DE MÉTRICA
    # Agora a conta vai funcionar!
    # Criamos a Eficiência de Kudos (Kudos/Hits)
    # Usamos o .replace(0, 1) no hits apenas para evitar divisão por zero
    df['eficiencia_kudos'] = (df['kudos'] / df['hits'].replace(0, 1)) * 100

    # 3. FILTRAGEM (Opcional: Focar no Leclerc)
    # Se quiser ver apenas fics que mencionam o Charles Leclerc
    fics_leclerc = df[df['character'].str.contains('Charles Leclerc', na=False, case=False)]

    # 4. EXIBIÇÃO DOS RESULTADOS
    print("\n--- TOP 5 HISTÓRIAS MAIS AMADAS (EFICIÊNCIA) ---")
    top_eficiencia = df.sort_values(by='eficiencia_kudos', ascending=False).head(5)
    print(top_eficiencia[['title', 'kudos', 'hits', 'eficiencia_kudos']])

    print("\n--- RESUMO GERAL DO FANDOM ---")
    print(f"Total de fics analisadas: {len(df)}")
    print(f"Média de palavras: {df['words'].mean():.0f}")
    print(f"Total de Kudos no Fandom: {df['kudos'].sum():.0f}")
    
    if not fics_leclerc.empty:
        print(f"Fics mencionando o Leclerc: {len(fics_leclerc)}")

if __name__ == "__main__":
    analisar_dados()