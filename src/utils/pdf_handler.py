import io
from pypdf import PdfReader, PdfWriter

def limpar_quebras_pdf(texto):
    """
    Remove quebras de linha simples (que são apenas quebras de layout do PDF) 
    mantendo as quebras duplas (parágrafos) e respeitando diálogos e listas.
    """
    if not texto:
        return ""
    
    # Normaliza quebras de linha
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    
    # Divide em linhas brutas
    linhas_brutas = texto.split('\n')
    
    linhas_limpas = []
    buffer_paragrafo = []
    
    for linha in linhas_brutas:
        linha_strip = linha.strip()
        
        # Se for linha vazia, fecha o parágrafo anterior
        if not linha_strip:
            if buffer_paragrafo:
                linhas_limpas.append(" ".join(buffer_paragrafo))
                buffer_paragrafo = []
            continue
            
        # Detecta início de diálogo ou marcador (—, -, •, *, “, ”, [, {, <)
        comeca_dialogo = linha_strip.startswith(('—', '-', '–', '"', '“', '”', '*', '•', '[', '{', '<'))
        
        # Se a nova linha inicia um diálogo/marcador, fecha o parágrafo anterior
        if comeca_dialogo and buffer_paragrafo:
            linhas_limpas.append(" ".join(buffer_paragrafo))
            buffer_paragrafo = []
            
        buffer_paragrafo.append(linha_strip)
        
        # Se a linha atual for muito curta (título, cabeçalho ou fala curta), fecha o parágrafo
        eh_linha_muito_curta = len(linha_strip) < 35
        
        # Se termina com pontuação típica e a linha original é curta
        termina_pontuacao = linha_strip.endswith(('.', '!', '?', '"', '”', '»', '*'))
        eh_linha_curta = len(linha_strip) < 50
        
        if eh_linha_muito_curta or (termina_pontuacao and eh_linha_curta):
            linhas_limpas.append(" ".join(buffer_paragrafo))
            buffer_paragrafo = []
            
    if buffer_paragrafo:
        linhas_limpas.append(" ".join(buffer_paragrafo))
        
    return "\n\n".join(linhas_limpas)

def extrair_texto_pdf(uploaded_file):
    """Extrai texto de um PDF enviado pelo usuário e limpa quebras de linha indesejadas."""
    reader = PdfReader(uploaded_file)
    texto_bruto = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            texto_bruto += t + "\n\n"
            
    # Executa a limpeza inteligente de quebras de layout do PDF
    texto_limpo = limpar_quebras_pdf(texto_bruto)
    return texto_limpo.strip()

def dividir_pdf(input_pdf_bytes, start_page, end_page):
    """Gera um novo PDF em memória contendo apenas as páginas do intervalo especificado."""
    reader = PdfReader(io.BytesIO(input_pdf_bytes))
    writer = PdfWriter()
    
    total_pages = len(reader.pages)
    start_idx = max(0, start_page - 1)
    end_idx = min(total_pages, end_page)
    
    for i in range(start_idx, end_idx):
        writer.add_page(reader.pages[i])
        
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer
