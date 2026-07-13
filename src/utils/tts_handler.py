import asyncio
import io
import edge_tts

def split_text(text, max_chars=3000):
    """Divide texto em chunks que o edge-tts consegue processar."""
    chunks = []
    paragraphs = text.split("\n\n")
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 > max_chars and current:
            chunks.append(current)
            current = para
        else:
            if current:
                current += "\n\n" + para
            else:
                current = para
            if len(current) > max_chars:
                sentences = current.replace("! ", "!|").replace("? ", "?|").replace(". ", ".|").split("|")
                piece = ""
                for s in sentences:
                    if len(piece) + len(s) > max_chars and piece:
                        chunks.append(piece)
                        piece = s
                    else:
                        piece += s
                if piece:
                    chunks.append(piece)
                current = ""
    if current:
        chunks.append(current)
    return [c for c in chunks if c.strip()]

async def sintetizar_chunk(chunk, voz, rate):
    """Sintetiza um único chunk de texto e retorna os bytes de áudio correspondentes."""
    communicate = edge_tts.Communicate(chunk, voz, rate=rate)
    chunk_buffer = io.BytesIO()
    async for part in communicate.stream():
        if part["type"] == "audio":
            chunk_buffer.write(part["data"])
    return chunk_buffer.getvalue()

async def gerar_audiobook_com_progresso(texto, voz, rate, progress_bar, status_text):
    """Gera áudio de forma concorrente (paralela) para todos os chunks e une tudo no final."""
    chunks = split_text(texto)
    total = len(chunks)
    
    if total == 0:
        return io.BytesIO()

    # Informar o início do processamento paralelo
    status_text.text(f"Iniciando síntese paralela de {total} bloco(s) de narração...")
    progress_bar.progress(0.1)

    # Disparar tarefas concorrentes usando asyncio.gather
    tasks = [sintetizar_chunk(chunk, voz, rate) for chunk in chunks]
    audio_chunks_bytes = await asyncio.gather(*tasks)

    # Concatenação e finalização
    progress_bar.progress(0.9)
    status_text.text("Concatenando faixas de áudio...")

    audio_buffer = io.BytesIO()
    for chunk_bytes in audio_chunks_bytes:
        audio_buffer.write(chunk_bytes)

    progress_bar.progress(1.0)
    status_text.text("Sintetizado com sucesso!")

    return audio_buffer

def run_async(coro):
    """Roda coroutine de forma compatível com Streamlit."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()
