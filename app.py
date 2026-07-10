import streamlit as st
import asyncio
import edge_tts
import io
import time
from pypdf import PdfReader, PdfWriter

# --- 0. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="AudioLivre Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ESTADO GLOBAL ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'texto_final' not in st.session_state:
    st.session_state.texto_final = ""
if 'voz' not in st.session_state:
    st.session_state.voz = "pt-BR-AntonioNeural"
if 'velocidade' not in st.session_state:
    st.session_state.velocidade = 1.0
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'deepseek_api_key' not in st.session_state:
    st.session_state.deepseek_api_key = ""
if 'contexto_livro' not in st.session_state:
    st.session_state.contexto_livro = ""
if 'instrucoes_traducao' not in st.session_state:
    st.session_state.instrucoes_traducao = ""
if 'deepseek_model' not in st.session_state:
    st.session_state.deepseek_model = "deepseek-chat"
if 'translation_style' not in st.session_state:
    st.session_state.translation_style = "Literário"

# --- ÍCONES (URLs Públicas Icons8 / Flaticon) ---
ICON_HEADER = "https://img.icons8.com/?size=100&id=h6KZp4Xmo1Je&format=png&color=000000"
ICON_IMPORT = "https://img.icons8.com/?size=100&id=kuOHmVeRoVF5&format=png&color=000000"
ICON_SPLIT = "https://img.icons8.com/?size=100&id=jVl18QnaGIE3&format=png&color=000000"
ICON_TRANSLATE = "https://img.icons8.com/?size=100&id=byau012HFa7I&format=png&color=000000"
ICON_VOICE = "https://cdn-icons-png.flaticon.com/512/709/709682.png"      # Microfone/Narrador (pode manter)
ICON_DOWNLOAD = "https://cdn-icons-png.flaticon.com/512/2874/2874802.png" # Download/Áudio (pode manter)

# Filtro de cor para imagens inline do cabeçalho e landing page
icon_filter = "filter: invert(1);" if st.session_state.dark_mode else "filter: none;"

# --- 1. DEFINIÇÃO DA PALETA DE CORES (VERMELHO E AMARELO) E TEMA ---
if st.session_state.dark_mode:
    # Modo Escuro (Fundo escuro profissional)
    bg_gradient = """
        background: radial-gradient(circle at 80% 20%, rgba(220, 38, 38, 0.12), transparent 50%),
                    radial-gradient(circle at 20% 80%, rgba(217, 119, 6, 0.08), transparent 50%),
                    #0f0909 !important;
        color: #f8fafc;
    """
    card_bg = "rgba(255, 255, 255, 0.02)"
    card_border = "rgba(255, 255, 255, 0.06)"
    text_color = "#f8fafc"
    subtitle_color = "#94a3b8"
    input_bg = "#1a1212"  # Fundo escuro para inputs
    input_border = "rgba(255, 255, 255, 0.1)"
    btn_text = "#ffffff"
    badge_bg = "rgba(255, 255, 255, 0.03)"
    badge_color = "#cbd5e1"
    nav_bg = "rgba(255, 255, 255, 0.02)"
    title_gradient = "linear-gradient(135deg, #ffffff, #dc2626, #d97706)"
else:
    # Modo Claro (Marfim Quente)
    bg_gradient = """
        background: radial-gradient(circle at 80% 20%, rgba(220, 38, 38, 0.08), transparent 50%),
                    radial-gradient(circle at 20% 80%, rgba(217, 119, 6, 0.06), transparent 50%),
                    #fdfbf7 !important;
        color: #1e1b4b;
    """
    card_bg = "rgba(0, 0, 0, 0.015)"
    card_border = "rgba(0, 0, 0, 0.08)"
    text_color = "#1e1b4b"
    subtitle_color = "#475569"
    input_bg = "#f5f3ef"  # Fundo claro para inputs
    input_border = "rgba(0, 0, 0, 0.12)"
    btn_text = "#ffffff"
    badge_bg = "rgba(0, 0, 0, 0.03)"
    badge_color = "#475569"
    nav_bg = "rgba(0, 0, 0, 0.02)"
    title_gradient = "linear-gradient(135deg, #1e1b4b, #dc2626, #d97706)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Fontes globais */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif;
    }}

    /* Fundo da aplicação */
    .stApp {{
        {bg_gradient}
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }}

    /* Estilização nativa dos containers com borda (Glassmorphism) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 1rem !important;
    }}

    /* Garante a visibilidade das labels dos inputs */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown h4 {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}

    /* Classe do Título para evitar bugs no background-clip de navegadores */
    .header-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        background: {title_gradient} !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block;
    }}

    /* Estilo do Hero da Landing Page */
    .hero-container {{
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
    }}
    .hero-badge {{
        display: inline-block;
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.15), rgba(217, 119, 6, 0.15));
        border: 1px solid rgba(217, 119, 6, 0.3);
        color: #d97706;
        padding: 0.35rem 1.2rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1.5rem;
    }}
    .hero-title {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, {text_color} 40%, #dc2626 70%, #d97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }}
    .hero-subtitle {{
        font-size: 1.2rem;
        color: {subtitle_color};
        max-width: 650px;
        margin: 0 auto 2.5rem auto;
        line-height: 1.6;
    }}

    /* Cards de Recursos */
    .feature-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 2.2rem 1.8rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }}
    .feature-card:hover {{
        background: rgba(220, 38, 38, 0.02);
        border-color: rgba(220, 38, 38, 0.3);
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(220, 38, 38, 0.08);
    }}
    .feature-card h3 {{
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
        color: {text_color};
    }}
    .feature-card p {{
        color: {subtitle_color};
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }}

    /* Custom badges */
    .info-badge {{
        display: inline-block;
        background: {badge_bg};
        color: {badge_color};
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid {card_border};
        font-weight: 500;
    }}

    /* Botão Customizado - Seletor específico para stButton para não afetar outros botões nativos */
    div[data-testid="stButton"] button {{
        background: linear-gradient(135deg, #dc2626, #d97706) !important;
        color: {btn_text} !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.25) !important;
        transition: all 0.25s ease !important;
        width: 100%;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(217, 119, 6, 0.35) !important;
        color: {btn_text} !important;
    }}

    /* Estilo robusto e legível para a caixa de texto (textarea) */
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"] {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
    }}
    div[data-testid="stTextArea"] div[data-baseweb="textarea"] {{
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
    }}

    /* Estilização legível e altamente visível para o File Uploader */
    div[data-testid="stFileUploader"] section {{
        background-color: {input_bg} !important;
        border: 1px dashed {input_border} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }}
    /* Forçar todos os textos dentro do uploader a usar a cor de texto visível */
    div[data-testid="stFileUploader"] section * {{
        color: {text_color} !important;
    }}
    /* Botão específico de upload dentro da dropzone */
    div[data-testid="stFileUploader"] section button {{
        background-color: {card_border} !important;
        color: {text_color} !important;
        border: 1px solid {input_border} !important;
        width: auto !important;
    }}
    div[data-testid="stFileUploader"] section button:hover {{
        background-color: {input_border} !important;
        border-color: #d97706 !important;
    }}

    /* Fallback para classes alternativas do uploader */
    div[data-testid="stFileUploaderDropzone"] {{
        background-color: {input_bg} !important;
        border: 1px dashed {input_border} !important;
    }}

    /* Corrigir cores dos inputs normais */
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {input_border} !important;
    }}
    input[type="text"], input[type="password"], input[type="number"] {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
    }}

    /* Estilo para barra de navegação */
    div[data-baseweb="segmented-control"] {{
        background-color: {nav_bg} !important;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid {card_border};
    }}

    .gradient-text {{
        background: linear-gradient(135deg, #dc2626, #d97706);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- Dicionário de Vozes Neurais ---
VOICES = {
    "pt-BR-ThalitaMultilingualNeural": "🇧🇷 Thalita (Feminina - Multilíngue)",
    "pt-BR-FranciscaNeural": "🇧🇷 Francisca (Feminina)",
    "pt-BR-AntonioNeural": "🇧🇷 Antonio (Masculina)",
    "pt-PT-RaquelNeural": "🇵🇹 Raquel (Feminina)",
    "pt-PT-DuarteNeural": "🇵🇹 Duarte (Masculina)",
    "en-US-AriaNeural": "🇺🇸 Aria (Feminina)",
    "en-US-GuyNeural": "🇺🇸 Guy (Masculina)",
    "es-ES-ElviraNeural": "🇪🇸 Elvira (Feminina)",
    "es-ES-AlvaroNeural": "🇪🇸 Alvaro (Masculina)"
}

# --- Dicionário de Prompts de Estilo de Tradução ---
STYLE_PROMPTS = {
    "Literário": "Mantenha um estilo literário/narrativo rico, priorizando a fluidez e a beleza das sentenças como se fosse um romance.",
    "Técnico/Formal": "Mantenha uma linguagem cirúrgica, técnica, objetiva e formal, traduzindo termos acadêmicos e científicos com precisão absoluta.",
    "Coloquial/Informal": "Priorize a naturalidade cotidiana da fala, mantendo expressões coloquiais adequadas, diálogos dinâmicos e fluidos."
}

# --- 3. FUNÇÕES AUXILIARES ---
def extrair_texto_pdf(uploaded_file):
    """Extrai texto de um PDF enviado pelo usuário."""
    reader = PdfReader(uploaded_file)
    texto = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            texto += t + "\n\n"
    return texto.strip()

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

async def gerar_audiobook_com_progresso(texto, voz, rate, progress_bar, status_text):
    """Gera áudio chunk por chunk atualizando a barra de progresso."""
    chunks = split_text(texto)
    total = len(chunks)
    audio_buffer = io.BytesIO()

    for i, chunk in enumerate(chunks):
        pct = i / total
        progress_bar.progress(pct)
        status_text.text(f"Sintetizando parte {i + 1} de {total}...")

        communicate = edge_tts.Communicate(chunk, voz, rate=rate)
        async for part in communicate.stream():
            if part["type"] == "audio":
                audio_buffer.write(part["data"])

        progress_bar.progress((i + 1) / total)

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

# --- 4. BARRA DE NAVEGAÇÃO SUPERIOR COM ALTERNADOR DE TEMA ---
col_title, col_theme = st.columns([4, 1.2])
with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
        <img src="{ICON_HEADER}" width="38" style="{icon_filter}" />
        <span class="header-title">AudioLivre Studio</span>
    </div>
    """, unsafe_allow_html=True)
with col_theme:
    theme_label = "Modo Claro" if st.session_state.dark_mode else "Modo Escuro"
    theme_icon = ":material/light_mode:" if st.session_state.dark_mode else ":material/dark_mode:"
    if st.button(theme_label, icon=theme_icon, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Barra de Navegação Separada
col_nav, col_split, col_trans, _ = st.columns([2.0, 1.2, 1.2, 0.4])
with col_nav:
    nav_options = {
        "home": ":material/home: Início", 
        "editor": ":material/edit_note: Editor de Texto", 
        "studio": ":material/spatial_audio: Estúdio de Áudio"
    }
    
    # Se o usuário estiver na aba do Tradutor ou do Divisor, a seleção ativa do segmented control fica vazia
    default_sel = st.session_state.page if st.session_state.page in nav_options else None
    
    selected_page = st.segmented_control(
        "Navegação",
        options=list(nav_options.keys()),
        format_func=lambda x: nav_options[x],
        label_visibility="collapsed",
        default=default_sel
    )
    if selected_page and selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

with col_split:
    # Botão do Divisor de PDF afastado e isolado na navegação
    is_splitter = (st.session_state.page == "splitter")
    if st.button("Divisor de PDF", icon=":material/content_cut:", use_container_width=True, type="primary" if is_splitter else "secondary"):
        st.session_state.page = "splitter"
        st.rerun()

with col_trans:
    # Botão do Tradutor DeepSeek afastado e isolado na navegação
    is_translator = (st.session_state.page == "translator")
    if st.button("Tradutor DeepSeek", icon=":material/translate:", use_container_width=True, type="primary" if is_translator else "secondary"):
        st.session_state.page = "translator"
        st.rerun()

st.divider()

# ==========================================
# PÁGINA 1: LANDING PAGE (🏠 Início)
# ==========================================
if st.session_state.page == "home":
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">Estúdio Profissional de Narração</div>
        <h1 class="hero-title">Seus PDFs em <span class="gradient-text">Audiolivros</span> de Alta Qualidade</h1>
        <p class="hero-subtitle">Utilize vozes neurais ultrarrealistas de inteligência artificial para ler, traduzir e converter seus documentos em MP3 de forma simples, elegante e totalmente gratuita.</p>
    </div>
    """, unsafe_allow_html=True)

    # Grid de Recursos (5 Colunas com Ícones Flaticon)
    col_feat1, col_feat2, col_feat3, col_feat4, col_feat5 = st.columns(5)
    
    with col_feat1:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_IMPORT}" width="54" style="{icon_filter} margin-bottom: 1.2rem;" />
            <h3>Importador Inteligente</h3>
            <p>Faça upload de documentos PDF e tenha todo o texto extraído de forma estruturada e imediata.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat2:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_SPLIT}" width="54" style="{icon_filter} margin-bottom: 1.2rem;" />
            <h3>Divisor de PDF</h3>
            <p>Divida arquivos grandes em blocos de 100 páginas ou intervalos customizados para facilitar o manuseio.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat3:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_TRANSLATE}" width="54" style="{icon_filter} margin-bottom: 1.2rem;" />
            <h3>Tradutor com IA</h3>
            <p>Traduza livros inteiros com a API do DeepSeek usando contextos e regras gramaticais personalizadas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat4:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_VOICE}" width="54" style="{icon_filter} margin-bottom: 1.2rem;" />
            <h3>Vozes Neurais de IA</h3>
            <p>Selecione entre diversas vozes com tons masculinos e femininos em português brasileiro, europeu e inglês.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat5:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_DOWNLOAD}" width="54" style="{icon_filter} margin-bottom: 1.2rem;" />
            <h3>Geração & Download</h3>
            <p>Sintetize grandes volumes de texto divididos em blocos e baixe o arquivo de áudio final em MP3.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # CTA Central
    col_cta_l, col_cta_c, col_cta_r = st.columns([1.5, 2, 1.5])
    with col_cta_c:
        if st.button("🚀 Entrar no Estúdio de Criação", use_container_width=True):
            st.session_state.page = "editor"
            st.rerun()

# ==========================================
# PÁGINA 2: EDITOR DE TEXTO (📖 Editor)
# ==========================================
elif st.session_state.page == "editor":
    st.markdown("### 📖 Editor e Extrator de Texto")
    st.caption("Faça upload de um PDF ou cole seu texto diretamente no editor de roteiro abaixo.")
    
    # Layout de Duas Colunas (Upload na esquerda, editor/resumo na direita)
    col_left, col_right = st.columns([1, 2.5])
    
    with col_left:
        with st.container(border=True):
            st.markdown("#### Carregar Documento")
            uploaded_pdf = st.file_uploader(
                "Arraste ou selecione seu arquivo PDF",
                type=["pdf"],
                label_visibility="collapsed"
            )
            
            if uploaded_pdf:
                with st.spinner("Extraindo texto do PDF..."):
                    texto_extraido = extrair_texto_pdf(uploaded_pdf)
                st.success(f"Sucesso: {len(texto_extraido):,} caracteres extraídos!")
                st.session_state.texto_final = texto_extraido
                st.session_state.editor_texto_area = texto_extraido

    with col_right:
        with st.container(border=True):
            st.markdown("#### Conteúdo do Roteiro")
            texto_editado = st.text_area(
                "Edite o roteiro:",
                value=st.session_state.texto_final,
                height=380,
                key="editor_texto_area",
                label_visibility="collapsed",
                placeholder="Cole seu texto aqui ou envie um PDF ao lado para começar..."
            )
            
            if st.button("💾 Salvar Roteiro", use_container_width=True):
                st.session_state.texto_final = texto_editado
                st.session_state.roteiro_final_area = texto_editado
                if texto_editado.strip():
                    st.success("Roteiro salvo com sucesso! Escolha o Tradutor DeepSeek ou o Estúdio de Áudio na barra superior.")
                else:
                    st.warning("O editor está vazio! Adicione algum texto antes de salvar.")

# ==========================================
# PÁGINA 3: TRADUTOR DEEPSEEK (🌐 Tradutor)
# ==========================================
elif st.session_state.page == "translator":
    st.markdown("### 🌐 Tradutor de PDF com IA (DeepSeek)")
    
    # Mensagem de "Em Desenvolvimento"
    st.markdown("""
    <div style="background: rgba(217, 119, 6, 0.1); border: 1px solid #d97706; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: left; font-size: 0.9rem; color: #f59e0b;">
        <strong>⚠️ FUNCIONALIDADE EM DESENVOLVIMENTO:</strong> A aba de tradução automática via API do DeepSeek está em fase de testes e refinamentos. Certifique-se de usar chaves de API válidas e com cota disponível.
    </div>
    """, unsafe_allow_html=True)

    st.caption("Faça upload de um PDF em Inglês ou traduza o texto do Editor usando a API do DeepSeek com instruções customizadas.")

    col_left, col_right = st.columns([1.2, 2])

    with col_left:
        with st.container(border=True):
            st.markdown("#### 1. Configurações da API")
            api_key = st.text_input(
                "DeepSeek API Key:",
                type="password",
                value=st.session_state.deepseek_api_key,
                placeholder="Insira sua chave sk-..."
            )
            st.session_state.deepseek_api_key = api_key

            # Seleção de Modelo
            api_model = st.selectbox(
                "Modelo de Tradução:",
                options=["deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: "DeepSeek V3 (Chat - Rápido)" if x == "deepseek-chat" else "DeepSeek R1 (Reasoner - Raciocínio Profundo)",
                index=0 if st.session_state.deepseek_model == "deepseek-chat" else 1
            )
            st.session_state.deepseek_model = api_model

            # Seleção de Tom / Estilo
            translation_style = st.selectbox(
                "Estilo/Tom da Tradução:",
                options=["Literário", "Técnico/Formal", "Coloquial/Informal"],
                index=["Literário", "Técnico/Formal", "Coloquial/Informal"].index(st.session_state.translation_style)
            )
            st.session_state.translation_style = translation_style

            st.markdown("---")
            st.markdown("#### 2. Carregar Novo PDF (Inglês)")
            uploaded_pdf = st.file_uploader(
                "Upload de PDF para Traduzir",
                type=["pdf"],
                key="translator_pdf_uploader",
                label_visibility="collapsed"
            )

            if uploaded_pdf:
                with st.spinner("Extraindo texto do PDF..."):
                    texto_extraido = extrair_texto_pdf(uploaded_pdf)
                st.success(f"PDF carregado: {len(texto_extraido):,} caracteres extraídos!")
                st.session_state.texto_final = texto_extraido
                st.session_state.translator_textarea = texto_extraido

        with st.container(border=True):
            st.markdown("#### 3. Prompts e Instruções")
            contexto = st.text_area(
                "Sobre o que é o livro (Contexto):",
                value=st.session_state.contexto_livro,
                placeholder="Ex: Livro de fantasia medieval sombria com foco em alquimia e combates.",
                height=100
            )
            st.session_state.contexto_livro = contexto

            instrucoes = st.text_area(
                "Instruções especiais de tradução:",
                value=st.session_state.instrucoes_traducao,
                placeholder="Ex: Traduza 'Mana' como 'Energia Espiritual'. Mantenha o tratamento formal 'vós' para a realeza.",
                height=120
            )
            st.session_state.instrucoes_traducao = instrucoes

    with col_right:
        with st.container(border=True):
            st.markdown("#### 4. Visualização do Texto para Traduzir")
            texto_original = st.text_area(
                "Texto para Traduzir:",
                value=st.session_state.texto_final,
                height=345,
                key="translator_textarea",
                label_visibility="collapsed",
                placeholder="O texto extraído do PDF ou digitado aparecerá aqui..."
            )
            st.session_state.texto_final = texto_original

        # Botão de Ação de Tradução
        if st.button("🌐 Iniciar Tradução com DeepSeek", use_container_width=True):
            if not api_key.strip():
                st.error("Por favor, insira uma DeepSeek API Key válida nas configurações.")
            elif not st.session_state.texto_final.strip():
                st.warning("Não há texto disponível para tradução. Envie um PDF ou digite algo.")
            else:
                chunks = split_text(st.session_state.texto_final, max_chars=2500)
                total_chunks = len(chunks)
                
                st.info(f"Iniciando tradução com o modelo {api_model} ({total_chunks} partes)...")
                progress_bar = st.progress(0, text="Conectando com DeepSeek...")
                status_text = st.empty()
                
                texto_traduzido_acumulado = []
                sucesso = True
                start_time = time.time()
                
                for i, chunk in enumerate(chunks):
                    status_text.text(f"Traduzindo parte {i+1} de {total_chunks}...")
                    progress_bar.progress(i / total_chunks)
                    
                    try:
                        import requests
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
                            st.error(f"Erro na parte {i+1}: Status {response.status_code} - {response.text}")
                            sucesso = False
                            break
                    except Exception as e:
                        st.error(f"Erro ao conectar com DeepSeek na parte {i+1}: {e}")
                        sucesso = False
                        break
                
                if sucesso:
                    total_duration = time.time() - start_time
                    progress_bar.progress(1.0, text="Concluído!")
                    status_text.text(f"Tradução finalizada em {total_duration:.1f} segundos!")
                    texto_final_traduzido = "\n\n".join(texto_traduzido_acumulado)
                    st.session_state.texto_final = texto_final_traduzido
                    st.session_state.roteiro_final_area = texto_final_traduzido
                    
                    st.success("Tudo pronto! O texto traduzido foi salvo. Vá para o Estúdio de Áudio para gravar a narração em português.")
                    
                    # Colunas para os botões de Download da tradução
                    col_dl_txt, col_dl_md, _ = st.columns([1.5, 1.5, 3])
                    with col_dl_txt:
                        st.download_button(
                            label="⬇️ Baixar como TXT",
                            data=texto_final_traduzido,
                            file_name="traducao.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col_dl_md:
                        st.download_button(
                            label="⬇️ Baixar como Markdown",
                            data=f"# Tradução - Audiobook\n\n{texto_final_traduzido}",
                            file_name="traducao.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with st.expander("Visualizar Texto Traduzido"):
                        st.text_area("Resultado:", value=texto_final_traduzido, height=250, disabled=True)

# ==========================================
# PÁGINA 4: DIVISOR DE PDF (✂️ Divisor)
# ==========================================
elif st.session_state.page == "splitter":
    st.markdown("### ✂️ Divisor de PDF")
    st.caption("Divida livros e documentos PDF grandes em blocos de 100 páginas (ou em lotes personalizados) para facilitar a tradução e gravação.")

    col_left, col_right = st.columns([1.2, 2])

    with col_left:
        with st.container(border=True):
            st.markdown("#### 1. Carregar PDF Grande")
            uploaded_pdf = st.file_uploader(
                "Selecione o PDF para dividir",
                type=["pdf"],
                key="splitter_pdf_uploader",
                label_visibility="collapsed"
            )

    with col_right:
        if not uploaded_pdf:
            st.info("💡 Por favor, faça o upload de um arquivo PDF na coluna da esquerda para começar a divisão.")
        else:
            # Ler metadados do PDF
            pdf_bytes = uploaded_pdf.read()
            reader = PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            file_name = uploaded_pdf.name
            file_size_mb = len(pdf_bytes) / (1024 * 1024)

            with st.container(border=True):
                st.markdown("#### 📊 Informações do Documento")
                st.markdown(
                    f'<span class="info-badge">Arquivo: {file_name}</span> '
                    f'<span class="info-badge">Tamanho: {file_size_mb:.2f} MB</span> '
                    f'<span class="info-badge">Total de Páginas: {total_pages}</span>',
                    unsafe_allow_html=True
                )

            # Escolha o modo de divisão
            with st.container(border=True):
                st.markdown("#### ⚙️ Modo de Divisão")
                modo_div = st.radio(
                    "Selecione o método de corte:",
                    ["Dividir de 100 em 100 páginas (Recomendado)", "Intervalo Personalizado"]
                )

                if modo_div == "Dividir de 100 em 100 páginas (Recomendado)":
                    st.markdown("##### 📦 Lotes de Páginas Gerados")
                    
                    # Gerar intervalos automáticos de 100 em 100
                    for start in range(1, total_pages + 1, 100):
                        end = min(start + 99, total_pages)
                        col_lote, col_btn = st.columns([2.2, 1.8])
                        with col_lote:
                            st.markdown(f"**Lote {start} a {end}** (Total: {end - start + 1} páginas)")
                        with col_btn:
                            try:
                                # Gera os bytes do PDF cortado em tempo de execução
                                split_buffer = dividir_pdf(pdf_bytes, start, end)
                                st.download_button(
                                    label=f"⬇️ Baixar Páginas {start}-{end}",
                                    data=split_buffer,
                                    file_name=f"{file_name.rsplit('.', 1)[0]}_paginas_{start}_{end}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_btn_{start}_{end}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Erro ao dividir: {e}")
                else:
                    st.markdown("##### 🛠️ Intervalo Customizado")
                    col_start, col_end = st.columns(2)
                    with col_start:
                        p_start = st.number_input("Página Inicial:", min_value=1, max_value=total_pages, value=1, step=1)
                    with col_end:
                        p_end = st.number_input("Página Final:", min_value=int(p_start), max_value=total_pages, value=min(int(p_start) + 99, total_pages), step=1)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if p_start > p_end:
                        st.error("A página inicial não pode ser maior que a página final.")
                    else:
                        try:
                            split_buffer = dividir_pdf(pdf_bytes, int(p_start), int(p_end))
                            st.download_button(
                                label=f"⬇️ Baixar PDF Customizado ({p_start}-{p_end})",
                                data=split_buffer,
                                file_name=f"{file_name.rsplit('.', 1)[0]}_paginas_{p_start}_{p_end}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Erro ao gerar intervalo customizado: {e}")

# ==========================================
# PÁGINA 5: ESTÚDIO DE ÁUDIO (🎙️ Estúdio)
# ==========================================
elif st.session_state.page == "studio":
    st.markdown("### 🎙️ Estúdio de Gravação e Síntese de Voz")
    
    if not st.session_state.texto_final.strip():
        st.info("⚠️ O roteiro está vazio. Envie um PDF, use o tradutor ou escreva algo na aba Editor de Texto antes de prosseguir.")
        if st.button("Ir para o Editor de Texto"):
            st.session_state.page = "editor"
            st.rerun()
    else:
        chars = len(st.session_state.texto_final)
        chunks_count = len(split_text(st.session_state.texto_final))
        
        # Badges informativos superiores
        st.markdown(
            f'<span class="info-badge">Roteiro: {chars:,} caracteres</span> '
            f'<span class="info-badge">~{chunks_count} blocos de narração</span>',
            unsafe_allow_html=True
        )
        
        # Ajustes e Preview lado a lado
        col_settings, col_preview = st.columns([1.2, 2])
        
        with col_settings:
            with st.container(border=True):
                st.markdown("#### Configurações da Voz")
                
                # Seletor de voz amigável
                selected_voice_key = st.selectbox(
                    "Escolha o Narrador:",
                    options=list(VOICES.keys()),
                    format_func=lambda x: VOICES[x],
                    index=list(VOICES.keys()).index(st.session_state.voz) if st.session_state.voz in VOICES else 0
                )
                st.session_state.voz = selected_voice_key
                
                # Controle de velocidade (Rate)
                velocidade_sel = st.slider(
                    "Velocidade de Fala:",
                    min_value=0.8,
                    max_value=1.3,
                    value=float(st.session_state.velocidade),
                    step=0.05
                )
                st.session_state.velocidade = velocidade_sel
                
                # Formatação do rate no padrão do edge-tts
                rate_val = round((velocidade_sel - 1) * 100)
                rate = f"+{rate_val}%" if rate_val >= 0 else f"{rate_val}%"
                
                st.markdown("<br>", unsafe_allow_html=True)
                genero = "masculina" if "Antonio" in selected_voice_key or "Duarte" in selected_voice_key or "Guy" in selected_voice_key or "Alvaro" in selected_voice_key else "feminina"
                st.markdown(
                    f'<div style="margin-top: 5px;">'
                    f'<span class="info-badge">Gênero: {genero}</span>'
                    f'<span class="info-badge">Ajuste de Velocidade: {rate}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with col_preview:
            with st.container(border=True):
                st.markdown("#### Visualização do Roteiro")
                roteiro_confirmado = st.text_area(
                    "Revisão do roteiro:",
                    value=st.session_state.texto_final,
                    height=260,
                    key="roteiro_final_area",
                    label_visibility="collapsed"
                )
                st.session_state.texto_final = roteiro_confirmado
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão de ação principal
        if st.button("⚡ Gerar Áudio Final (MP3)", use_container_width=True):
            progress_bar = st.progress(0, text="Iniciando sintetização...")
            status_text = st.empty()
            
            try:
                # Executa a geração assíncrona
                resultado = run_async(
                    gerar_audiobook_com_progresso(st.session_state.texto_final, selected_voice_key, rate, progress_bar, status_text)
                )
                
                if resultado.getbuffer().nbytes > 0:
                    status_text.text("Audiolivro sintetizado com sucesso!")
                    progress_bar.progress(1.0, text="Concluído!")
                    
                    with st.container(border=True):
                        st.markdown("#### Ouvir e Baixar seu Audiolivro")
                        
                        col_audio, col_dl = st.columns([3, 1])
                        with col_audio:
                            st.audio(resultado.getvalue())
                        with col_dl:
                            st.download_button(
                                label="⬇️ Baixar MP3",
                                data=resultado.getvalue(),
                                file_name="audiolivre.mp3",
                                mime="audio/mp3",
                                type="primary",
                                use_container_width=True
                            )
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Erro ao gerar áudio: {e}")

# --- 5. RODAPÉ DE CRÉDITOS ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
footer_color = "#94a3b8" if st.session_state.dark_mode else "#475569"
st.markdown(f"""
<div style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 0.9rem; color: {footer_color}; padding-bottom: 2rem; border-top: 1px solid {card_border}; padding-top: 1.5rem;">
    Desenvolvido com 🎧 por <a href="https://github.com/Paulogsilva28" target="_blank" style="color: #dc2626; font-weight: 700; text-decoration: none; border-bottom: 1px dashed #d97706;">Paulo Silva</a>
</div>
""", unsafe_allow_html=True)
