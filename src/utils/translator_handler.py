import requests
import time
from src.config import STYLE_PROMPTS
from src.utils.tts_handler import split_text

def traduzir_texto_deepseek(api_key, api_model, translation_style, contexto, instrucoes, texto_completo, progress_bar, status_text):
    """Realiza o loop de tradução do texto via DeepSeek API com barra de progresso."""
    chunks = split_text(texto_completo, max_chars=2500)
    total_chunks = len(chunks)
    
    texto_traduzido_acumulado = []
    start_time = time.time()
    
    for i, chunk in enumerate(chunks):
        status_text.text(f"Traduzindo parte {i+1} de {total_chunks}...")
        progress_bar.progress(i / total_chunks)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        system_prompt = f"""Você é um tradutor profissional de livros do Inglês para o Português Brasileiro (pt-BR).
O livro tem o seguinte contexto geral:
{contexto}

Estilo e Tom da Tradução:
{STYLE_PROMPTS.get(translation_style, "Literário")}

Instruções especiais de tradução a seguir estritamente:
{instrucoes}

Mantenha a fidelidade, fluidez de leitura, parágrafos e o tom original correspondente. Não invente explicações, não inclua notas e retorne APENAS o texto traduzido final."""

        payload = {
            "model": api_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk}
            ]
        }
        
        if api_model == "deepseek-chat":
            payload["temperature"] = 0.3
            
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload,
            timeout=90
        )
        
        if response.status_code == 200:
            res_json = response.json()
            translated_chunk = res_json["choices"][0]["message"]["content"].strip()
            texto_traduzido_acumulado.append(translated_chunk)
        else:
            raise Exception(f"Erro na parte {i+1}: Status {response.status_code} - {response.text}")
            
    total_duration = time.time() - start_time
    texto_final = "\n\n".join(texto_traduzido_acumulado)
    return texto_final, total_duration
