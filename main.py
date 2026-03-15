import os
import requests
from dotenv import load_dotenv
import ollama
import re

load_dotenv()
# Configurações
SERPER_KEY = os.getenv("SERPER_API_KEY") # Lembre-se de revogar essa chave depois!
MODELO_IA = "InvestigAI-Bot" # <-- MUDA AQUI! Agora chamamos o seu modelo customizado

def buscar_evidencias_atualizadas(noticia):
    url = "https://google.serper.dev/search"
    
    # Termos de controle para o Serper trazer fact-checking
    query_refinada = f"{noticia} status atual 2026 verificação de fatos"
    
    payload = {
        "q": query_refinada,
        "gl": "br",
        "hl": "pt-br",
        "num": 5
    }
    
    headers = {
        'X-API-KEY': SERPER_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json().get('organic', [])
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []

def analisar_veracidade_blindada(noticia, evidencias):
    # Organiza os snippets
    contexto = "\n".join([f"FONTE: {item['title']}\nCONTEÚDO: {item['snippet']}" for item in evidencias])

    # <-- OLHA COMO O PROMPT FICOU LIMPO! -->
    # Todas as regras (neutralidade, formato de saída, etc) já estão no Modelfile.
    # Aqui a gente só manda a variável da notícia e as evidências.
    prompt_dinamico = f"""
    NOTÍCIA A SER VERIFICADA: "{noticia}"
    
    EVIDÊNCIAS COLETADAS NA INTERNET AGORA:
    {contexto}
    """

    try:
        response = ollama.chat(model=MODELO_IA, messages=[
            {'role': 'user', 'content': prompt_dinamico}
        ])
        
        conteudo = response['message']['content']
        
        # Opcional: Limpar a tag <think> do DeepSeek para o usuário final
        resposta_limpa = re.sub(r'<think>.*?</think>', '', conteudo, flags=re.DOTALL).strip()
        
        return resposta_limpa

    except Exception as e:
        return f"Erro no Ollama: {e}"

# --- EXECUÇÃO DO TESTE ---
pergunta = "Presidente lula morreu?"
print(f"Processando análise com o ValidaBot para: {pergunta}...\n")

dados_web = buscar_evidencias_atualizadas(pergunta)
if dados_web:
    resultado = analisar_veracidade_blindada(pergunta, dados_web)
    print("=== RESULTADO DA ANÁLISE ===")
    print(resultado)
else:
    print("Não foi possível coletar evidências.")