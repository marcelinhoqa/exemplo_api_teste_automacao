import sqlite3
from models.user import User, UserResponse  # Modelo User
from db import Db
from datetime import datetime
import pytz
import bcrypt
from models.user_dto import UserDto

class UserDb:
    def __init__(self):
        self.db = Db()  # Sua classe Db que gerencia a conexão com o banco de dados

    def insert(self, user: User):
        try:
            # Gerando o hash da senha
            hashed_password = bcrypt.hashpw(user.senha.encode('utf-8'), bcrypt.gensalt())

            with self.db.get_cursor() as cursor:
                brasil_tz = pytz.timezone('America/Sao_Paulo')
                hora_atual = datetime.now(brasil_tz)
                hora_atual_formatada = hora_atual.strftime('%Y-%m-%d %H:%M:%S')

                # Começando uma transação
                cursor.execute('BEGIN TRANSACTION;')

                # Inserir o usuário 
                cursor.execute(''' 
                    INSERT INTO usuario (email, senha, status, data_criacao, data_atualizacao)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user.email, hashed_password, user.status, hora_atual_formatada, hora_atual_formatada))

                # Capturar o ID gerado para o novo usuário
                user_id = cursor.lastrowid

                # Commit da transação
                self.db.connect.commit()

                return user_id

        except sqlite3.IntegrityError as e:
            self.db.connect.rollback()  # Rollback em caso de erro
            raise ValueError("Erro: Email já cadastrado ou dados inválidos.")
        except Exception as e:
            self.db.connect.rollback()  # Rollback em caso de erro
            raise ValueError(f"Erro ao inserir usuário: {str(e)}")

    def get(self, user_id: int) -> UserDto:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute('SELECT * FROM usuario WHERE id = ?', (user_id,))
                row = cursor.fetchone()

            if row:
                return UserDto(
                    id=row[0],                # índice 0: id
                    email=row[1],             # índice 1: email
                    status=row[3],            # índice 3: status
                    data_criacao=row[4],      # índice 4: data_criacao
                    data_atualizacao=row[5]   # índice 5: data_atualizacao
                )
            return None  # Retorna None se não encontrar o usuário
        except Exception as e:
            raise ValueError(f"Erro ao buscar usuário: {str(e)}")


    def update(self, user_id: int, user: User):
        try:
            with self.db.get_cursor() as cursor:
                brasil_tz = pytz.timezone('America/Sao_Paulo')
                hora_atual = datetime.now(brasil_tz)
                hora_atual_formatada = hora_atual.strftime('%Y-%m-%d %H:%M:%S')

                # Verifica se o usuário existe antes de tentar atualizá-lo
                cursor.execute('SELECT * FROM usuario WHERE id = ?', (user_id,))
                row = cursor.fetchone()

                if not row:
                    raise ValueError(f"Usuário com ID {user_id} não encontrado.")

                # Verifica se a senha foi fornecida, se sim, atualiza a senha
                if user.senha:
                    hashed_password = bcrypt.hashpw(user.senha.encode('utf-8'), bcrypt.gensalt())
                else:
                    hashed_password = row[2]  # Mantém a senha antiga se não houver nova

                # Atualiza o usuário no banco
                cursor.execute(''' 
                    UPDATE usuario 
                    SET email = ?, senha = ?, status = ?, data_atualizacao = ?
                    WHERE id = ?
                ''', (user.email, hashed_password, user.status, hora_atual_formatada, user_id))

                # Commit para salvar as mudanças
                self.db.connect.commit()

        except sqlite3.IntegrityError as e:
            raise ValueError("Este e-mail já está em uso por outro usuário.")
        except Exception as e:
            raise ValueError(f"Erro ao atualizar usuário: {str(e)}")

    def find_by_email(self, email: str) -> User:
        try:
            email = email.strip()  # Remove espaços extras
            with self.db.get_cursor() as cursor:
                cursor.execute('SELECT * FROM usuario WHERE email = ?', (email,))
                row = cursor.fetchone() 
                print("oi")
                print(row)

            if row:
                return User(
                    id=row[0],                # índice 0: id
                    email=row[1],             # índice 1: email
                    senha=row[2],   
                    status=row[3],            # índice 3: status
                    data_criacao=row[4],      # índice 4: data_criacao
                    data_atualizacao=row[5]   # índice 5: data_atualizacao
                )
            return None  # Retorna None se não encontrar o usuário
        except Exception as e:
            raise ValueError(f"Erro ao buscar usuário por e-mail: {str(e)}")



    def get_all(self) -> list[UserDto]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM usuario")  #
                rows = cursor.fetchall()  # Obtém todas as linhas

            # Converte as linhas para UserDto
            return [
                UserDto(
                    id=row[0],                # índice 0: id
                    email=row[1],             # índice 1: email
                    status=row[3],            # índice 3: status
                    data_criacao=row[4],      # índice 4: data_criacao
                    data_atualizacao=row[5]   # índice 5: data_atualizacao
                ) for row in rows
            ]
        except Exception as e:
            raise ValueError(f"Erro ao buscar os usuários: {str(e)}")


    def delete(self, user_id: int):
        try:
            with self.db.get_cursor() as cursor:
                # Verifica se o usuário existe
                cursor.execute('SELECT * FROM usuario WHERE id = ?', (user_id,))
                row = cursor.fetchone()

                if not row:
                    raise ValueError(f"Usuário com ID {user_id} não encontrado.")

                # Deleta o usuário
                cursor.execute('DELETE FROM usuario WHERE id = ?', (user_id,))

                # Commit para salvar a exclusão
                self.db.connect.commit()
        except Exception as e:
            raise ValueError(f"Erro ao excluir usuário: {str(e)}")
