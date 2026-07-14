import streamlit as st
from src.utils.pdf_handler import extrair_texto_pdf
from src.utils.translator_handler import traduzir_texto_deepseek
from src.utils.tts_handler import run_async

def render_translator():
    # Sincroniza o estado do texto de tradução ao entrar na página
    if "translator_textarea" not in st.session_state or not st.session_state.translator_textarea:
        if "texto_final" in st.session_state and st.session_state.texto_final:
            st.session_state.translator_textarea = st.session_state.texto_final

    st.markdown("### :material/translate: Tradutor de PDF com IA (Gemini / DeepSeek / Google)")
    
    # Mensagem informativa sobre gratuidade e consumo
    st.markdown("""
    <div style="background: rgba(217, 119, 6, 0.1); border: 1px solid #d97706; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: left; font-size: 0.9rem; color: #f59e0b;">
        <strong>ECONOMIA E SEGURANÇA:</strong> Escolha o <strong>Google Translate</strong> para traduções 100% gratuitas e sem limites. Escolha o <strong>Gemini 2.5 Flash</strong> para traduções literárias profundas 100% gratuitas (basta gerar sua chave grátis no Google AI Studio).
    </div>
    """, unsafe_allow_html=True)

    st.caption("Faça upload de um PDF em Inglês ou cole o texto para tradução direta em Português.")

    col_left, col_right = st.columns([1.2, 2])

    with col_left:
        with st.container(border=True):
            st.markdown("#### 1. Configurações da API")
            
            # Seleção de Modelo
            api_model = st.selectbox(
                "Modelo de Tradução:",
                options=["google", "gemini-3.5-flash", "deepseek-chat", "deepseek-reasoner"],
                format_func=lambda x: {
                    "google": "Google Translate (Gratuito - Sem Chave)",
                    "gemini-3.5-flash": "Gemini 3.5 Flash (Gratuito - Com Chave)",
                    "deepseek-chat": "DeepSeek V3 (Chat - Rápido)",
                    "deepseek-reasoner": "DeepSeek R1 (Reasoner - Raciocínio)"
                }[x],
                index=["google", "gemini-3.5-flash", "deepseek-chat", "deepseek-reasoner"].index(st.session_state.deepseek_model) if st.session_state.deepseek_model in ["google", "gemini-3.5-flash", "deepseek-chat", "deepseek-reasoner"] else 0
            )
            st.session_state.deepseek_model = api_model

            # Configuração e Ocultação Inteligente da Chave de API
            api_key = ""
            if api_model == "gemini-3.5-flash":
                if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip():
                    api_key = st.secrets["GEMINI_API_KEY"]
                    st.success("🔒 Chave API do Gemini autenticada pelo servidor!")
                else:
                    api_key = st.text_input(
                        "Gemini API Key:",
                        type="password",
                        value=st.session_state.gemini_api_key,
                        placeholder="Insira sua chave AIzaSy..."
                    )
                    st.session_state.gemini_api_key = api_key
            elif api_model in ["deepseek-chat", "deepseek-reasoner"]:
                if "DEEPSEEK_API_KEY" in st.secrets and st.secrets["DEEPSEEK_API_KEY"].strip():
                    api_key = st.secrets["DEEPSEEK_API_KEY"]
                    st.success("🔒 Chave API do DeepSeek autenticada pelo servidor!")
                else:
                    api_key = st.text_input(
                        "DeepSeek API Key:",
                        type="password",
                        value=st.session_state.deepseek_api_key,
                        placeholder="Insira sua chave sk-..."
                    )
                    st.session_state.deepseek_api_key = api_key
            
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
                st.session_state.pdf_filename = uploaded_pdf.name

        with st.container(border=True):
            st.markdown("#### 3. Prompts e Instruções (IA)")
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
        if api_model == "google":
            btn_label = "Iniciar Tradução Gratuita"
        elif api_model == "gemini-3.5-flash":
            btn_label = "Iniciar Tradução com Gemini"
        else:
            btn_label = "Iniciar Tradução com DeepSeek"

        if st.button(btn_label, icon=":material/translate:", use_container_width=True):
            if api_model == "gemini-3.5-flash" and not api_key.strip():
                st.error("Por favor, insira uma Gemini API Key válida nas configurações.")
            elif api_model in ["deepseek-chat", "deepseek-reasoner"] and not api_key.strip():
                st.error("Por favor, insira uma DeepSeek API Key válida nas configurações.")
            elif not st.session_state.texto_final.strip():
                st.warning("Não há texto disponível para tradução. Envie um PDF ou digite algo.")
            else:
                progress_bar = st.progress(0, text="Preparando tradução...")
                status_text = st.empty()
                st.session_state.translated_text = None
                
                try:
                    # Executa a tradução assíncrona concorrente em paralelo
                    texto_final_traduzido, total_duration = run_async(
                        traduzir_texto_deepseek(
                            api_key, api_model, translation_style, contexto, instrucoes, 
                            st.session_state.texto_final, progress_bar, status_text
                        )
                    )
                    
                    progress_bar.progress(1.0, text="Concluído!")
                    status_text.text(f"Tradução finalizada em {total_duration:.1f} segundos!")
                    st.session_state.texto_final = texto_final_traduzido
                    st.session_state.roteiro_final_area = texto_final_traduzido
                    st.session_state.translated_text = texto_final_traduzido
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Ocorreu um erro durante a tradução: {e}")
                    st.session_state.translated_text = None

        # Exibe as ações de download e navegação se houver tradução salva no estado global
        if "translated_text" in st.session_state and st.session_state.translated_text:
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("Tudo pronto! O texto traduzido foi salvo. Vá para o Estúdio de Áudio para gravar a narração em português.")
            
            # Colunas para os botões de Download da tradução e navegação
            col_dl_txt, col_dl_md, col_nav_studio = st.columns([1.5, 1.5, 2])
            with col_dl_txt:
                st.download_button(
                    label="Baixar como TXT",
                    icon=":material/download:",
                    data=st.session_state.translated_text,
                    file_name="traducao.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_dl_md:
                st.download_button(
                    label="Baixar como Markdown",
                    icon=":material/download:",
                    data=f"# Tradução - Audiobook\n\n{st.session_state.translated_text}",
                    file_name="traducao.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col_nav_studio:
                if st.button("Estúdio de Gravação", icon=":material/spatial_audio:", use_container_width=True, type="primary"):
                    st.session_state.page = "studio"
                    st.rerun()
            
            with st.expander("Visualizar Texto Traduzido", icon=":material/menu_book:"):
                st.text_area("Resultado:", value=st.session_state.translated_text, height=250, disabled=True)
