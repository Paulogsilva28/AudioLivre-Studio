import streamlit as st

# --- ÍCONES (URLs Públicas Icons8 / Flaticon) ---
ICON_HEADER = "https://img.icons8.com/?size=100&id=h6KZp4Xmo1Je&format=png&color=000000"
ICON_IMPORT = "https://img.icons8.com/?size=100&id=kuOHmVeRoVF5&format=png&color=000000"
ICON_SPLIT = "https://img.icons8.com/?size=100&id=jVl18QnaGIE3&format=png&color=000000"
ICON_TRANSLATE = "https://img.icons8.com/?size=100&id=byau012HFa7I&format=png&color=000000"
ICON_VOICE = "https://cdn-icons-png.flaticon.com/512/709/709682.png"      # Microfone/Narrador
ICON_DOWNLOAD = "https://cdn-icons-png.flaticon.com/512/2874/2874802.png" # Download/Áudio

# --- DICIONÁRIO DE VOZES NEURAIS ---
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

# --- DICIONÁRIO DE PROMPTS DE ESTILO DE TRADUÇÃO ---
STYLE_PROMPTS = {
    "Literário": "Mantenha um estilo literário/narrativo rico, priorizando a fluidez e a beleza das sentenças como se fosse um romance.",
    "Técnico/Formal": "Mantenha uma linguagem cirúrgica, técnica, objetiva e formal, traduzindo termos acadêmicos e científicos com precisão absoluta.",
    "Coloquial/Informal": "Priorize a naturalidade cotidiana da fala, mantendo expressões coloquiais adequadas, diálogos dinâmicos e fluidos."
}

def get_theme_colors(dark_mode):
    """Retorna a paleta de cores correspondente ao tema."""
    if dark_mode:
        return {
            "bg_gradient": """
                background: radial-gradient(circle at 80% 20%, rgba(220, 38, 38, 0.12), transparent 50%),
                            radial-gradient(circle at 20% 80%, rgba(217, 119, 6, 0.08), transparent 50%),
                            #0f0909 !important;
                color: #f8fafc;
            """,
            "card_bg": "rgba(255, 255, 255, 0.02)",
            "card_border": "rgba(255, 255, 255, 0.06)",
            "text_color": "#f8fafc",
            "subtitle_color": "#94a3b8",
            "input_bg": "#1a1212",
            "input_border": "rgba(255, 255, 255, 0.1)",
            "btn_text": "#ffffff",
            "badge_bg": "rgba(255, 255, 255, 0.03)",
            "badge_color": "#cbd5e1",
            "nav_bg": "rgba(255, 255, 255, 0.02)",
            "title_gradient": "linear-gradient(135deg, #ffffff, #dc2626, #d97706)"
        }
    else:
        return {
            "bg_gradient": """
                background: radial-gradient(circle at 80% 20%, rgba(220, 38, 38, 0.08), transparent 50%),
                            radial-gradient(circle at 20% 80%, rgba(217, 119, 6, 0.06), transparent 50%),
                            #fdfbf7 !important;
                color: #1e1b4b;
            """,
            "card_bg": "rgba(0, 0, 0, 0.015)",
            "card_border": "rgba(0, 0, 0, 0.08)",
            "text_color": "#1e1b4b",
            "subtitle_color": "#475569",
            "input_bg": "#f5f3ef",
            "input_border": "rgba(0, 0, 0, 0.12)",
            "btn_text": "#ffffff",
            "badge_bg": "rgba(0, 0, 0, 0.03)",
            "badge_color": "#475569",
            "nav_bg": "rgba(0, 0, 0, 0.02)",
            "title_gradient": "linear-gradient(135deg, #1e1b4b, #dc2626, #d97706)"
        }

def inject_global_css(dark_mode):
    """Injeta as regras globais de CSS no Streamlit."""
    c = get_theme_colors(dark_mode)
    
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
            {c['bg_gradient']}
        }}

        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }}

        /* Estilização nativa dos containers com borda (Glassmorphism) */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: {c['card_bg']} !important;
            border: 1px solid {c['card_border']} !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            backdrop-filter: blur(12px) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 1rem !important;
        }}

        /* Garante a visibilidade das labels dos inputs */
        div[data-testid="stWidgetLabel"] p, label, .stMarkdown h4 {{
            color: {c['text_color']} !important;
            font-weight: 600 !important;
        }}

        /* Classe do Título para evitar bugs no background-clip de navegadores */
        .header-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            background: {c['title_gradient']} !important;
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
            background: linear-gradient(135deg, {c['text_color']} 40%, #dc2626 70%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }}
        .hero-subtitle {{
            font-size: 1.2rem;
            color: {c['subtitle_color']};
            max-width: 650px;
            margin: 0 auto 2.5rem auto;
            line-height: 1.6;
        }}

        /* Cards de Recursos */
        .feature-card {{
            background: {c['card_bg']};
            border: 1px solid {c['card_border']};
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
            color: {c['text_color']};
        }}
        .feature-card p {{
            color: {c['subtitle_color']};
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 0;
        }}

        /* Custom badges */
        .info-badge {{
            display: inline-block;
            background: {c['badge_bg']};
            color: {c['badge_color']};
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
            border: 1px solid {c['card_border']};
            font-weight: 500;
        }}

        /* Botão Customizado - Seletor específico para stButton para não afetar outros botões nativos */
        div[data-testid="stButton"] button {{
            background: linear-gradient(135deg, #dc2626, #d97706) !important;
            color: {c['btn_text']} !important;
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
            color: {c['btn_text']} !important;
        }}

        /* Estilo robusto e legível para a caixa de texto (textarea) */
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextArea"] div[data-baseweb="textarea"],
        div[data-testid="stTextArea"] div[data-baseweb="base-input"] {{
            background-color: {c['input_bg']} !important;
            color: {c['text_color']} !important;
        }}
        div[data-testid="stTextArea"] div[data-baseweb="textarea"] {{
            border: 1px solid {c['input_border']} !important;
            border-radius: 8px !important;
        }}

        /* Estilização legível e altamente visível para o File Uploader */
        div[data-testid="stFileUploader"] section {{
            background-color: {c['input_bg']} !important;
            border: 1px dashed {c['input_border']} !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
        }}
        /* Forçar todos os textos dentro do uploader a usar a cor de texto visível */
        div[data-testid="stFileUploader"] section * {{
            color: {c['text_color']} !important;
        }}
        /* Botão específico de upload dentro da dropzone */
        div[data-testid="stFileUploader"] section button {{
            background-color: {c['card_border']} !important;
            color: {c['text_color']} !important;
            border: 1px solid {c['input_border']} !important;
            width: auto !important;
        }}
        div[data-testid="stFileUploader"] section button:hover {{
            background-color: {c['input_border']} !important;
            border-color: #d97706 !important;
        }}

        /* Fallback para classes alternativas do uploader */
        div[data-testid="stFileUploaderDropzone"] {{
            background-color: {c['input_bg']} !important;
            border: 1px dashed {c['input_border']} !important;
        }}

        /* Corrigir cores dos inputs normais */
        div[data-baseweb="select"] > div {{
            background-color: {c['input_bg']} !important;
            color: {c['text_color']} !important;
            border-color: {c['input_border']} !important;
        }}
        input[type="text"], input[type="password"], input[type="number"] {{
            background-color: {c['input_bg']} !important;
            color: {c['text_color']} !important;
            border: 1px solid {c['input_border']} !important;
            border-radius: 8px !important;
        }}

        /* Estilo para barra de navegação */
        div[data-baseweb="segmented-control"] {{
            background-color: {c['nav_bg']} !important;
            border-radius: 12px;
            padding: 4px;
            border: 1px solid {c['card_border']};
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


def get_icon_filter(dark_mode):
    """Retorna a string de filtro CSS para inverter cores de ícones pretos em modo escuro."""
    return "filter: invert(1);" if dark_mode else "filter: none;"

