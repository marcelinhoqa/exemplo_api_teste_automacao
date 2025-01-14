from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class User(BaseModel):
    email: str
    senha: str
    status: Optional[str] = "ativo"
    data_criacao: Optional[datetime] = None  # Campo opcional
    data_atualizacao: Optional[datetime] = None  # Campo opcional

    @validator('email')
    def email_nao_vazio(cls, v):
        if not v:
            raise ValueError('Informe um e-mail')
        return v
    
    @validator('senha')
    def senha_nao_vazio(cls, v):
        if not v:
            raise ValueError('Informe uma senha')
        return v

class UserResponse(User):
    senha: Optional[str] = None  # Sobrescreve o campo 'senha' para não ser retornado.
    
class User(User):
    #id: int  # O campo 'id' deve ser incluído aqui para retornar o 'id'
    id: Optional[int] = None

    class Config:
        orm_mode = True  # Para permitir a conversão automática de ORM para Pydantic
