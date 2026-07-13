import streamlit as st
import io
from pypdf import PdfReader
from src.utils.pdf_handler import dividir_pdf

def render_splitter():
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
