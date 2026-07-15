import requests
import time
import asyncio
import hashlib
import streamlit as st
from src.config import STYLE_PROMPTS
from src.utils.tts_handler import split_text
from deep_translator import GoogleTranslator

def call_deepseek_api(api_key, api_model, system_prompt, chunk):
    """Realiza a chamada HTTP síncrona para a API da DeepSeek com retry inteligente."""
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
        
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=90
            )
            if response.status_code == 200:
                res_json = response.json()
                return res_json["choices"][0]["message"]["content"].strip()
            
            # Tenta novamente em caso de limite de requisições ou erros temporários de servidor
            elif response.status_code in [429, 502, 503, 504] and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Status {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 5)
                continue
            raise e

def call_gemini_api(api_key, system_prompt, chunk):
    """Realiza a chamada HTTP síncrona para a API do Gemini 3.5 Flash com retry inteligente."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{
            "parts": [{"text": chunk}]
        }],
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.3
        }
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            if response.status_code == 200:
                res_json = response.json()
                try:
                    return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError):
                    raise Exception(f"Resposta inválida da API do Gemini: {response.text}")
            
            # Se for erro temporário de servidor (503) ou excesso de taxa (429), tenta novamente com backoff
            elif response.status_code in [429, 503] and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Status {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 5)
                continue
            raise e

async def traduzir_texto_deepseek(api_key, api_model, translation_style, contexto, instrucoes, texto_completo, progress_bar, status_text):
    """Realiza a tradução de todo o texto de forma concorrente em paralelo com cache MD5 inteligente."""
    # Define o tamanho do bloco dependendo do modelo (Gemini aceita blocos maiores de 12k caracteres)
    max_chars = 12000 if api_model == "gemini-3.5-flash" else 2500
    chunks = split_text(texto_completo, max_chars=max_chars)
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        return "", 0.0

    if 'translation_cache' not in st.session_state:
        st.session_state.translation_cache = {}

    status_text.text("Analisando texto e validando cache...")
    progress_bar.progress(0.05)
    
    # Prompt do Sistema para o DeepSeek/Gemini
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
        if api_model == "gemini-3.5-flash":
            # Tradução sequencial com controle estrito de taxa (5 RPM) para o plano gratuito do Gemini
            resolved_translations = []
            total_tasks = len(tasks_to_run)
            for idx, t in enumerate(tasks_to_run):
                pct = 0.2 + (0.7 * (idx / total_tasks))
                pct_display = int((idx / total_tasks) * 100)
                status_text.text(f"Traduzindo lote {idx+1}/{total_tasks} ({pct_display}%) com Gemini...")
                progress_bar.progress(pct, text=f"Traduzindo: {idx+1}/{total_tasks} partes ({pct_display}%)")
                
                # Executa a chamada
                translation = await asyncio.to_thread(call_gemini_api, api_key, system_prompt, t[1])
                resolved_translations.append(translation)
                
                # Aguarda 13 segundos entre as requisições se não for o último lote, para garantir que não ultrapasse a taxa de 5 requisições por minuto (5 RPM)
                if idx < total_tasks - 1:
                    status_text.text(f"Aguardando 13s para respeitar limite de cota gratuita (RPM)...")
                    await asyncio.sleep(13)
        else:
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
                
            # Mapeia as coroutines com o índice
            async def run_with_idx(idx, coro):
                res = await coro
                return idx, res
                
            tasks_with_idx = [run_with_idx(i, run_with_sem(c)) for i, c in enumerate(coroutines)]
            
            resolved_translations = [None] * len(tasks_to_run)
            completed = 0
            for future in asyncio.as_completed(tasks_with_idx):
                idx, translation = await future
                resolved_translations[idx] = translation
                completed += 1
                
                pct = 0.2 + (0.7 * (completed / len(tasks_to_run)))
                pct_display = int((completed / len(tasks_to_run)) * 100)
                progress_bar.progress(
                    min(pct, 0.9),
                    text=f"Traduzindo: {completed}/{len(tasks_to_run)} partes ({pct_display}%)"
                )
                status_text.text(f"Traduzindo com IA... {pct_display}% completo ({completed} de {len(tasks_to_run)} partes)")
        
        # Guardar no cache e preencher o array de resultados ordenados
        for idx, (original_idx, chunk, chunk_hash) in enumerate(tasks_to_run):
            translated_text = resolved_translations[idx]
            st.session_state.translation_cache[chunk_hash] = translated_text
            results[original_idx] = translated_text

    total_duration = time.time() - start_time
    texto_final = "\n\n".join(results)
    
    return texto_final, total_duration
