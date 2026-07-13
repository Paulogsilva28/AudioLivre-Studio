import io
from pypdf import PdfReader, PdfWriter

def extrair_texto_pdf(uploaded_file):
    """Extrai texto de um PDF enviado pelo usuário."""
    reader = PdfReader(uploaded_file)
    texto = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            texto += t + "\n\n"
    return texto.strip()

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
