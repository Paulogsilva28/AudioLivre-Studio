import requests
import time
import asyncio
import hashlib
import streamlit as st
from src.config import STYLE_PROMPTS
from src.utils.tts_handler import split_text
from deep_translator import GoogleTranslator

def call_deepseek_api(api_key, api_model, system_prompt, chunk):
    """Realiza a chamada HTTP síncrona para a API da DeepSeek."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
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
        return res_json["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"Status {response.status_code} - {response.text}")

async def traduzir_texto_deepseek(api_key, api_model, translation_style, contexto, instrucoes, texto_completo, progress_bar, status_text):
    """Realiza a tradução de todo o texto de forma concorrente em paralelo com cache MD5 inteligente."""
    chunks = split_text(texto_completo, max_chars=2500)
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        return "", 0.0

    if 'translation_cache' not in st.session_state:
        st.session_state.translation_cache = {}

    status_text.text("Analisando texto e validando cache...")
    progress_bar.progress(0.05)
    
    # Prompt do Sistema para o DeepSeek
    system_prompt = f"""Você é um tradutor profissional de livros do Inglês para o Português Brasileiro (pt-BR).
O livro tem o seguinte contexto geral:
{contexto}

Estilo e Tom da Tradução:
{STYLE_PROMPTS.get(translation_style, "Literário")}

Instruções especiais de tradução a seguir estritamente:
{instrucoes}

Mantenha a fidelidade, fluidez de leitura, parágrafos e o tom original correspondente. Não invente explicações, não inclua notas e retorne APENAS o texto traduzido final."""

    start_time = time.time()
    
    results = [None] * total_chunks
    tasks_to_run = []  # Lista de tuplas: (index_original, chunk, hash)

    # Identificar quais blocos de texto precisam ser traduzidos e quais vêm do cache
    for i, chunk in enumerate(chunks):
        # A chave do cache inclui o modelo, estilo e instruções para evitar falsos positivos
        cache_key_raw = f"{chunk}_{api_model}_{translation_style}_{contexto}_{instrucoes}"
        chunk_hash = hashlib.md5(cache_key_raw.encode('utf-8')).hexdigest()
        
        if chunk_hash in st.session_state.translation_cache:
            results[i] = st.session_state.translation_cache[chunk_hash]
        else:
            tasks_to_run.append((i, chunk, chunk_hash))

    if tasks_to_run:
        status_text.text(f"Traduzindo {len(tasks_to_run)} parte(s) não cacheada(s) em paralelo...")
        progress_bar.progress(0.2)
        
        # Limita a no máximo 3 requisições simultâneas para evitar bloqueio por excesso de taxa (Rate Limits)
        semaphore = asyncio.Semaphore(3)

        async def run_with_sem(coro):
            async with semaphore:
                return await coro

        # Despachar chamadas baseando-se no modelo escolhido
        if api_model == "google":
            # Tradução gratuita usando Google Translator via deep-translator em threads concorrentes
            coroutines = [
                asyncio.to_thread(
                    lambda text: GoogleTranslator(source='auto', target='pt').translate(text),
                    t[1]
                )
                for t in tasks_to_run
            ]
        else:
            # Tradução via DeepSeek API
            coroutines = [
                asyncio.to_thread(call_deepseek_api, api_key, api_model, system_prompt, t[1])
                for t in tasks_to_run
            ]
            
        # Executar todas as requisições em paralelo concorrente controlado por semáforo
        tasks = [run_with_sem(c) for c in coroutines]
        resolved_translations = await asyncio.gather(*tasks)
        
        # Guardar no cache e preencher o array de resultados ordenados
        for idx, (original_idx, chunk, chunk_hash) in enumerate(tasks_to_run):
            translated_text = resolved_translations[idx]
            st.session_state.translation_cache[chunk_hash] = translated_text
            results[original_idx] = translated_text

    total_duration = time.time() - start_time
    texto_final = "\n\n".join(results)
    
    return texto_final, total_duration
