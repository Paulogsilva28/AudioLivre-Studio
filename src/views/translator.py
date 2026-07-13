import streamlit as st
from src.utils.pdf_handler import extrair_texto_pdf
from src.utils.translator_handler import traduzir_texto_deepseek

def render_translator():
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
                progress_bar = st.progress(0, text="Conectando com DeepSeek...")
                status_text = st.empty()
                
                try:
                    texto_final_traduzido, total_duration = traduzir_texto_deepseek(
                        api_key, api_model, translation_style, contexto, instrucoes, 
                        st.session_state.texto_final, progress_bar, status_text
                    )
                    
                    progress_bar.progress(1.0, text="Concluído!")
                    status_text.text(f"Tradução finalizada em {total_duration:.1f} segundos!")
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
                        
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Ocorreu um erro durante a tradução: {e}")
