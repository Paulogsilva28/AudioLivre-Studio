import sqlite3
import datetime

DB_PATH = "audiolivre.db"

def get_connection():
    """Retorna uma conexão aberta com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Ativa acesso por nome de coluna
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria a tabela audiobooks se ela não existir no banco."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audiobooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            texto_original TEXT,
            texto_traduzido TEXT,
            audio_bytes BLOB NOT NULL,
            narrador TEXT,
            velocidade REAL
        )
    """)
    conn.commit()
    conn.close()

def salvar_audiobook(titulo, texto_original, texto_traduzido, audio_bytes, narrador, velocidade):
    """Insere um novo audiobook gravado no banco de dados SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    data_criacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO audiobooks (titulo, data_criacao, texto_original, texto_traduzido, audio_bytes, narrador, velocidade)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (titulo, data_criacao, texto_original, texto_traduzido, audio_bytes, narrador, velocidade))
    conn.commit()
    conn.close()

def listar_audiobooks():
    """Retorna todos os audiobooks registrados (sem carregar o BLOB do áudio por motivos de performance)."""
    conn = get_connection()
    cursor = conn.cursor()
    # Não selecionamos a coluna 'audio_bytes' para carregar a lista instantaneamente
    cursor.execute("""
        SELECT id, titulo, data_criacao, length(texto_original) as len_orig, length(texto_traduzido) as len_trad, narrador, velocidade 
        FROM audiobooks 
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def obter_audiobook(project_id):
    """Retorna o registro completo de um audiobook (incluindo áudio e textos) pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audiobooks WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def excluir_audiobook(project_id):
    """Deleta o registro do audiobook do banco de dados pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audiobooks WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
