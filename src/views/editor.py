import streamlit as st
from src.utils.pdf_handler import extrair_texto_pdf

def render_editor():
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
