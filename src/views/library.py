import streamlit as st
from src.utils.db_handler import listar_audiobooks, obter_audiobook, excluir_audiobook

def render_library():
    st.markdown("### :material/library_books: Biblioteca de Audiobooks")
    st.caption("Veja, reproduza e baixe seus audiobooks gravados anteriormente.")
    
    projects = listar_audiobooks()
    
    if not projects:
        st.info("Sua biblioteca está vazia por enquanto! Vá para o Estúdio de Áudio, gere um MP3 e salve-o para vê-lo aqui.")
        return
        
    # Seletor de Projetos salvos
    project_options = {p['id']: f"{p['titulo']} ({p['data_criacao']})" for p in projects}
    selected_id = st.selectbox(
        "Selecione um Audiobook salvo:",
        options=list(project_options.keys()),
        format_func=lambda x: project_options[x]
    )
    
    if selected_id:
        # Carregar os dados detalhados (incluindo o BLOB de áudio) do banco
        project = obter_audiobook(selected_id)
        
        col_info, col_actions = st.columns([2, 1])
        
        with col_info:
            with st.container(border=True):
                st.markdown(f"#### :material/info: Detalhes: {project['titulo']}")
                st.markdown(
                    f'<span class="info-badge">Data de Gravação: {project["data_criacao"]}</span> '
                    f'<span class="info-badge">Narrador: {project["narrador"]}</span> '
                    f'<span class="info-badge">Velocidade: {project["velocidade"]}x</span>',
                    unsafe_allow_html=True
                )
                
                st.markdown("##### :material/volume_up: Ouvir Audiobook")
                st.audio(project['audio_bytes'])
                
        with col_actions:
            with st.container(border=True):
                st.markdown("#### :material/settings: Ações do Projeto")
                
                # Download do MP3
                st.download_button(
                    label="Baixar Áudio (MP3)",
                    icon=":material/download:",
                    data=project['audio_bytes'],
                    file_name=f"{project['titulo'].lower().replace(' ', '_')}.mp3",
                    mime="audio/mp3",
                    use_container_width=True,
                    type="primary"
                )
                
                # Download do texto final/traduzido se existir
                if project['texto_traduzido']:
                    st.download_button(
                        label="Baixar Tradução (.txt)",
                        icon=":material/download:",
                        data=project['texto_traduzido'],
                        file_name=f"{project['titulo'].lower().replace(' ', '_')}_traducao.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                # Botão de Excluir
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Excluir Projeto", icon=":material/delete:", use_container_width=True):
                    excluir_audiobook(selected_id)
                    st.success(f"Projeto '{project['titulo']}' excluído da biblioteca!")
                    st.rerun()
                    
        # Visualização dos Roteiros expandida
        with st.expander("Ver Roteiros de Texto", icon=":material/menu_book:"):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("**Texto Original:**")
                st.text_area("Original:", value=project['texto_original'] or "", height=250, disabled=True, key="lib_orig")
            with col_t2:
                st.markdown("**Texto Traduzido (Roteiro Narração):**")
                st.text_area("Traduzido:", value=project['texto_traduzido'] or "", height=250, disabled=True, key="lib_trad")
