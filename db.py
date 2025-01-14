import sqlite3
from contextlib import contextmanager

class Db:
    def __init__(self, db_file='repository/treinamento.db'):
        self.db_file = db_file
        self.connect = None
        self.cursor = None

    def connect_db(self):
        """Estabelece uma conexão com o banco de dados e retorna a conexão."""
        if self.connect is None:
            self.connect = sqlite3.connect(self.db_file, timeout=10, check_same_thread=False)
            self.connect.execute('PRAGMA journal_mode=WAL;')  # Habilita o WAL
            self.cursor = self.connect.cursor()
        return self.connect  # Retorna a conexão para ser usada no contexto 'with'

    # Adicionando o gerenciador de contexto para o cursor
    # Gerenciador de contexto para cursor
    @contextmanager
    def get_cursor(self):
        """Gerenciador de contexto para fornecer um cursor."""
        connection = self.connect_db()  # Conectando-se ao banco de dados
        cursor = connection.cursor()  # Criando o cursor
        try:
            yield cursor  # Passa o cursor para uso externo
        finally:
            cursor.close()  # Garante que o cursor seja fechado após o uso
            # Não fechamos a conexão aqui porque ela pode ser usada em outras consulta

    def set_wal_mode(self):
            """Configura o banco de dados para usar o modo WAL (Write-Ahead Logging)."""
            with self.get_cursor() as cursor:
                cursor.execute('PRAGMA journal_mode = WAL;')  # Define o modo WAL
                print("Modo WAL ativado com sucesso.")
                
    def commit(self):
        if self.connect:
            self.connect.commit()

    def rollback(self):
        if self.connect:
            self.connect.rollback()

    def close(self):
        if self.connect:
            self.connect.close()
            self.connect = None
            self.cursor = None

    @contextmanager
    def get_connection(self):
        """Garante que cada operação tenha sua própria conexão isolada"""
        conn = sqlite3.connect(self.db_file, timeout=10, check_same_thread=False)
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()
            
    def execute(self, query, params=()):
            """Executa a consulta utilizando a conexão gerenciada"""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor

    def create_tables(self):
        self.connect_db()

        # Tabela admin
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                status TEXT DEFAULT 'ativo',  -- Campo 'status' com valor padrão 'ativo'
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Campo de data de criação
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.connect.commit()
        self.connect.close()

# Implementando os métodos __enter__ e __exit__ para o protocolo de contexto
    def __enter__(self):
        """Inicia a conexão ao banco e retorna a própria instância de Db."""
        self.connect_db()  # Conecta ao banco de dados
        return self  # Retorna a instância para ser usada dentro do contexto

    def __exit__(self, exc_type, exc_value):
        """Fechamento da conexão e tratamento de exceções se necessário."""
        if exc_type is not None:
            # Se houve erro, você pode realizar algum tratamento aqui, como logar
            print(f"Ocorreu um erro: {exc_value}")
        if self.connect:
            self.connect.commit()  # Faz o commit das transações
            self.connect.close()   # Fecha a conexão ao banco