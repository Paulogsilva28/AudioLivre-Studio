import streamlit as st
from src.config import ICON_IMPORT, ICON_SPLIT, ICON_TRANSLATE, ICON_VOICE, ICON_DOWNLOAD, get_icon_filter

def render_home(dark_mode):
    current_filter = get_icon_filter(dark_mode)

    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">Estúdio Profissional de Narração</div>
        <h1 class="hero-title">Seus PDFs em <span class="gradient-text">Audiolivros</span> de Alta Qualidade</h1>
        <p class="hero-subtitle">Utilize vozes neurais ultrarrealistas de inteligência artificial para ler, traduzir e converter seus documentos em MP3 de forma simples, elegante e totalmente gratuita.</p>
    </div>
    """, unsafe_allow_html=True)

    # Grid de Recursos (5 Colunas com Ícones)
    col_feat1, col_feat2, col_feat3, col_feat4, col_feat5 = st.columns(5)
    
    with col_feat1:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_IMPORT}" width="54" style="{current_filter} margin-bottom: 1.2rem;" />
            <h3>Importador Inteligente</h3>
            <p>Faça upload de documentos PDF e tenha todo o texto extraído de forma estruturada e imediata.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat2:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_SPLIT}" width="54" style="{current_filter} margin-bottom: 1.2rem;" />
            <h3>Divisor de PDF</h3>
            <p>Divida arquivos grandes em blocos de 100 páginas ou intervalos customizados para facilitar o manuseio.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat3:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_TRANSLATE}" width="54" style="{current_filter} margin-bottom: 1.2rem;" />
            <h3>Tradutor com IA</h3>
            <p>Traduza livros inteiros com a API do DeepSeek usando contextos e regras gramaticais personalizadas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat4:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_VOICE}" width="54" style="{current_filter} margin-bottom: 1.2rem;" />
            <h3>Vozes Neurais de IA</h3>
            <p>Selecione entre diversas vozes com tons masculinos e femininos em português brasileiro, europeu e inglês.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat5:
        st.markdown(f"""
        <div class="feature-card">
            <img src="{ICON_DOWNLOAD}" width="54" style="{current_filter} margin-bottom: 1.2rem;" />
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
