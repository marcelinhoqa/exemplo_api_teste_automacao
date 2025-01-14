from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserDto(BaseModel):
    id: int  # Adicionar o campo id
    email: str
    status: Optional[str] = "ativo"
    data_criacao: Optional[datetime] = None  # Campo opcional
    data_atualizacao: Optional[datetime] = None  # Campo opcional
    
    class Config:
        orm_mode = True  # Para permitir a conversão automática de ORM para Pydantic
