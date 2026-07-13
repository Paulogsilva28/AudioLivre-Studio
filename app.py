import streamlit as st
from src.config import inject_global_css, ICON_HEADER, get_icon_filter
from src.views.home import render_home
from src.views.editor import render_editor
from src.views.translator import render_translator
from src.views.splitter import render_splitter
from src.views.studio import render_studio

# --- 0. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="AudioLivre Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. ESTADO GLOBAL ---
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

# --- 2. INJEÇÃO DE ESTILOS CSS ---
inject_global_css(st.session_state.dark_mode)

# --- 3. BARRA DE NAVEGAÇÃO SUPERIOR COM ALTERNADOR DE TEMA ---
col_title, col_theme = st.columns([4, 1.2])
with col_title:
    # Obtém o filtro dinâmico do config correspondente ao modo escuro ativo
    current_filter = get_icon_filter(st.session_state.dark_mode)
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
        <img src="{ICON_HEADER}" width="38" style="{current_filter}" />
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
    
    # Mantém o menu atualizado com a página ativa se ela estiver listada no menu segmentado
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
    is_splitter = (st.session_state.page == "splitter")
    if st.button("Divisor de PDF", icon=":material/content_cut:", use_container_width=True, type="primary" if is_splitter else "secondary"):
        st.session_state.page = "splitter"
        st.rerun()

with col_trans:
    is_translator = (st.session_state.page == "translator")
    if st.button("Tradutor DeepSeek", icon=":material/translate:", use_container_width=True, type="primary" if is_translator else "secondary"):
        st.session_state.page = "translator"
        st.rerun()

st.divider()

# --- 4. ROTEAMENTO DINÂMICO ---
if st.session_state.page == "home":
    render_home(st.session_state.dark_mode)
elif st.session_state.page == "editor":
    render_editor()
elif st.session_state.page == "translator":
    render_translator()
elif st.session_state.page == "splitter":
    render_splitter()
elif st.session_state.page == "studio":
    render_studio()

# --- 5. RODAPÉ DE CRÉDITOS ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
footer_color = "#94a3b8" if st.session_state.dark_mode else "#475569"
border_color = "rgba(255, 255, 255, 0.06)" if st.session_state.dark_mode else "rgba(0, 0, 0, 0.08)"
st.markdown(f"""
<div style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 0.9rem; color: {footer_color}; padding-bottom: 2rem; border-top: 1px solid {border_color}; padding-top: 1.5rem;">
    Desenvolvido com 🎧 por <a href="https://github.com/Paulogsilva28" target="_blank" style="color: #dc2626; font-weight: 700; text-decoration: none; border-bottom: 1px dashed #d97706;">Paulo Silva</a>
</div>
""", unsafe_allow_html=True)
