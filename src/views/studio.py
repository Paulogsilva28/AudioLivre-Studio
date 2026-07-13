import streamlit as st
from src.config import VOICES
from src.utils.tts_handler import split_text, gerar_audiobook_com_progresso, run_async

def render_studio():
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
                    st.session_state.audio_resultado_bytes = resultado.getvalue()
                    st.session_state.audio_resultado_voice = selected_voice_key
                    st.session_state.audio_resultado_speed = velocidade_sel
                    status_text.text("Audiolivro sintetizado com sucesso!")
                    progress_bar.progress(1.0, text="Concluído!")
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Erro ao gerar áudio: {e}")
                st.session_state.audio_resultado_bytes = None

        # Exibir player e formulário de salvamento se houver áudio gerado ativo na sessão
        if "audio_resultado_bytes" in st.session_state and st.session_state.audio_resultado_bytes:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("#### Ouvir e Baixar seu Audiolivro")
                
                col_audio, col_dl = st.columns([3, 1])
                with col_audio:
                    st.audio(st.session_state.audio_resultado_bytes)
                with col_dl:
                    st.download_button(
                        label="⬇️ Baixar MP3",
                        data=st.session_state.audio_resultado_bytes,
                        file_name="audiolivre.mp3",
                        mime="audio/mp3",
                        type="primary",
                        use_container_width=True
                    )
                
                st.divider()
                st.markdown("##### 💾 Salvar na Biblioteca Local")
                col_title_input, col_save_btn = st.columns([3.2, 1.8])
                with col_title_input:
                    project_title = st.text_input(
                        "Nome do Projeto / Livro:", 
                        value="", 
                        placeholder="Ex: Capítulo 1 - O Início",
                        label_visibility="collapsed",
                        key="save_project_title_input"
                    )
                with col_save_btn:
                    if st.button("Salvar na Biblioteca", use_container_width=True):
                        if not project_title.strip():
                            st.warning("Digite um título!")
                        else:
                            from src.utils.db_handler import salvar_audiobook
                            texto_orig = st.session_state.get("translator_textarea", "") or st.session_state.texto_final
                            texto_trad = st.session_state.texto_final
                            saved_voice = st.session_state.get("audio_resultado_voice", selected_voice_key)
                            saved_speed = st.session_state.get("audio_resultado_speed", velocidade_sel)
                            
                            try:
                                salvar_audiobook(
                                    titulo=project_title.strip(),
                                    texto_original=texto_orig,
                                    texto_traduzido=texto_trad,
                                    audio_bytes=st.session_state.audio_resultado_bytes,
                                    narrador=saved_voice,
                                    velocidade=saved_speed
                                )
                                st.success("🎉 Salvo com sucesso na Biblioteca!")
                            except Exception as db_err:
                                st.error(f"Erro ao salvar: {db_err}")
