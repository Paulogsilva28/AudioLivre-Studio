# 🎧 AudioLivre Studio

**AudioLivre Studio** é uma plataforma web premium e moderna desenvolvida em Python para transformar seus documentos PDF e textos em audiolivros (audiobooks) de alta fidelidade usando inteligência artificial.

O projeto conta com um design escuro sofisticado com efeito de **Glassmorphism (vidro)**, suporte a temas Claro e Escuro, e integrações poderosas para facilitar a sua leitura e audição.

---

## 🚀 Recursos Principais

### 🏠 1. Apresentação (Landing Page)
* Interface moderna com tipografia elegante (Google Fonts: *Outfit* e *Inter*).
* Apresentação rápida e intuitiva dos recursos do estúdio.
* Acesso imediato à área de criação.

### 📖 2. Editor de Roteiro e Extrator de PDF
* Faça upload de qualquer arquivo PDF para extrair o texto automaticamente em tempo de execução.
* Editor de texto integrado para ajustar o roteiro, remover cabeçalhos/rodapés e personalizar a leitura.

### 🌐 3. Tradutor com IA (Integração DeepSeek)
* Traduza livros e PDFs inteiros do Inglês para o Português utilizando o modelo `deepseek-chat` da API do **DeepSeek**.
* Caixa de contexto para você explicar o tema do livro à IA.
* Espaço de instruções customizadas para termos técnicos, tratamento de realeza, glossários e regras de tradução.
* Processamento segmentado e barra de progresso visual em tempo real.

### ✂️ 4. Divisor de PDF Integrado
* Divida PDFs de livros muito extensos de **100 em 100 páginas** de forma 100% automática.
* Suporte a recorte por intervalo de páginas personalizado.
* Fatiamento e compilação de PDFs executados diretamente na memória RAM (In-Memory) para downloads instantâneos e seguros sem salvar arquivos temporários no servidor.

### 🎙️ 5. Estúdio de Voz Neural (Text-to-Speech)
* Catálogo amplo de narradores neurais da Microsoft (Edge TTS) em Português (Brasil e Portugal), Inglês e Espanhol.
* Suporte à nova voz premium multilingual `pt-BR-ThalitaMultilingualNeural`.
* Controle de velocidade da fala com barra deslizante.
* Streaming de síntese de áudio por partes com barra de progresso.
* Player nativo e botão de download imediato em **MP3** de alta qualidade.

---

## 🌓 Tema Claro e Escuro
A aplicação conta com um alternador inteligente de temas (`Modo Claro` / `Modo Escuro`) que altera dinamicamente todo o design do CSS do aplicativo com cores personalizadas (Vinho e Amarelo Âmbar) e contraste perfeitamente testado em inputs e file uploaders.

---

## 🛠️ Tecnologias Utilizadas
* **Backend & Frontend**: [Streamlit](https://streamlit.io/)
* **Conversão de Voz**: [Edge-TTS](https://github.com/rany2/edge-tts)
* **Manipulação de PDF**: [PyPDF](https://pypdf.readthedocs.io/)
* **Requisições de IA**: [Requests](https://requests.readthedocs.io/)

---

## 💻 Instalação e Execução Local

### Pré-requisitos
* Python 3.10 ou superior instalado na máquina.

### Passo a Passo

1. **Clonar o Repositório**
   ```bash
   git clone git@github.com:Paulogsilva28/projeto-python.git
   cd projeto-python
   ```

2. **Criar e Ativar Ambiente Virtual (Recomendado)**
   * No Windows:
     ```bash
     py -m venv .venv
     .venv\Scripts\activate
     ```
   * No Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar Dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a Aplicação**
   ```bash
   streamlit run app.py
   ```

---

## 👤 Autor
Desenvolvido com 🎧 por [Paulo Silva](https://github.com/Paulogsilva28).
