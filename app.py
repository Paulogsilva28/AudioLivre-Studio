import streamlit as st
import asyncio
import edge_tts
import io
from pypdf import PdfReader

# --- 0. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Audiobook Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. CSS CUSTOMIZADO PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Fontes globais */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
    }

    /* Fundo da aplicação */
    .stApp {
        background: radial-gradient(circle at 80% 20%, rgba(138, 43, 226, 0.15), transparent 50%),
                    radial-gradient(circle at 20% 80%, rgba(0, 255, 255, 0.1), transparent 50%),
                    #0b0b14 !important;
        color: #e2e8f0;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Painéis de vidro (Glassmorphism) */
    .glass-panel {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Estilo do Hero da Landing Page */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(0, 255, 255, 0.2));
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #00ffff;
        padding: 0.35rem 1.2rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1.5rem;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #ffffff 40%, #c084fc 70%, #22d3ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        max-width: 650px;
        margin: 0 auto 2.5rem auto;
        line-height: 1.6;
    }

    /* Cards de Recursos */
    .feature-card {
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 2.2rem 1.8rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(138, 43, 226, 0.3);
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(138, 43, 226, 0.08);
    }
    .feature-icon {
        font-size: 2.8rem;
        margin-bottom: 1.2rem;
    }
    .feature-card h3 {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
        color: #f1f5f9;
    }
    .feature-card p {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }

    /* Custom badges */
    .info-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.03);
        color: #cbd5e1;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        font-weight: 500;
    }

    /* Botão Customizado */
    div.stButton > button {
        background: linear-gradient(135deg, #8a2be2, #00ffff) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.25) !important;
        transition: all 0.25s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 255, 255, 0.35) !important;
        color: #ffffff !important;
    }

    /* Botões Secundários */
    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #e2e8f0 !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* Customizações de inputs Streamlit */
    textarea {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    textarea:focus {
        border-color: #00ffff !important;
    }

    /* Ocultar elements padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. ESTADO GLOBAL ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'texto_final' not in st.session_state:
    st.session_state.texto_final = ""
if 'voz' not in st.session_state:
    st.session_state.voz = "pt-BR-AntonioNeural"
if 'velocidade' not in st.session_state:
    st.session_state.velocidade = 1.0

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

# --- 4. BARRA DE NAVEGAÇÃO SUPERIOR ---
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 2.25rem;">🎧</span>
        <span style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #ffffff, #c084fc, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Audiobook Studio</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Abas de Navegação usando Segmented Control de forma customizada e limpa
col_nav, _ = st.columns([2, 1])
with col_nav:
    nav_options = {"home": "🏠 Início", "editor": "📖 Editor de Texto", "studio": "🎙️ Estúdio de Áudio"}
    selected_page = st.segmented_control(
        "Navegação",
        options=list(nav_options.keys()),
        format_func=lambda x: nav_options[x],
        label_visibility="collapsed",
        default=st.session_state.page
    )
    if selected_page and selected_page != st.session_state.page:
        st.session_state.page = selected_page
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
        <h1 class="hero-title">Seus PDFs em <span class="gradient-text">Audiobooks</span> de Alta Qualidade</h1>
        <p class="hero-subtitle">Utilize vozes neurais ultrarrealistas de inteligência artificial para ler e converter seus documentos em MP3 de forma simples, elegante e totalmente gratuita.</p>
    </div>
    """, unsafe_allow_html=True)

    # Grid de Recursos
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <h3>Importador Inteligente</h3>
            <p>Faça upload de documentos PDF e tenha todo o texto extraído de forma estruturada e imediata.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <h3>Vozes Neurais de IA</h3>
            <p>Selecione entre diversas vozes com tons masculinos e femininos em português brasileiro, europeu e inglês.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
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
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
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
            if not st.session_state.texto_final:
                st.session_state.texto_final = texto_extraido
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("#### Conteúdo do Roteiro")
        texto_editado = st.text_area(
            "Edite o roteiro:",
            value=st.session_state.texto_final,
            height=380,
            key="editor_texto_area",
            label_visibility="collapsed",
            placeholder="Cole seu texto aqui ou envie um PDF ao lado para começar..."
        )
        
        if st.button("💾 Salvar Roteiro e ir para Gravação", use_container_width=True):
            st.session_state.texto_final = texto_editado
            if texto_editado.strip():
                st.session_state.page = "studio"
                st.rerun()
            else:
                st.warning("O editor está vazio! Adicione algum texto antes de salvar.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PÁGINA 3: ESTÚDIO DE ÁUDIO (🎙️ Estúdio)
# ==========================================
elif st.session_state.page == "studio":
    st.markdown("### 🎙️ Estúdio de Gravação e Síntese de Voz")
    
    if not st.session_state.texto_final.strip():
        st.info("⚠️ O roteiro está vazio. Envie um PDF ou escreva algo na aba Editor de Texto antes de prosseguir.")
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
            st.markdown('<div class="glass-panel" style="height: 100%;">', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)

        with col_preview:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown("#### Visualização do Roteiro")
            roteiro_confirmado = st.text_area(
                "Revisão do roteiro:",
                value=st.session_state.texto_final,
                height=260,
                key="roteiro_final_area",
                label_visibility="collapsed"
            )
            st.session_state.texto_final = roteiro_confirmado
            st.markdown('</div>', unsafe_allow_html=True)
            
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
                    status_text.text("Audiobook sintetizado com sucesso!")
                    progress_bar.progress(1.0, text="Concluído!")
                    
                    st.markdown('<div class="glass-panel" style="margin-top: 2rem;">', unsafe_allow_html=True)
                    st.markdown("#### Ouvir e Baixar seu Audiobook")
                    
                    col_audio, col_dl = st.columns([3, 1])
                    with col_audio:
                        st.audio(resultado.getvalue())
                    with col_dl:
                        st.download_button(
                            label="⬇️ Baixar MP3",
                            data=resultado.getvalue(),
                            file_name="audiobook.mp3",
                            mime="audio/mp3",
                            type="primary",
                            use_container_width=True
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Erro ao gerar áudio: {e}")
