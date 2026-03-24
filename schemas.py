from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ProdutoBase(BaseModel):
    """Schema base - campos comuns"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do produto")
    preco: float = Field(..., gt=0, description="Preço deve ser maior que zero")
    quantidade: int = Field(0, ge=0, description="Quantidade em estoque")
   
    @validator('preco')
    def preco_nao_pode_ser_zero(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v
   
    @validator('nome')
    def nome_nao_pode_ser_vazio(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Nome não pode ser vazio')
        return v.strip()


class ProdutoCreate(ProdutoBase):
    """Schema para CRIAR produto"""
    pass


class ProdutoUpdate(BaseModel):
    """Schema para ATUALIZAR produto (todos os campos são opcionais)"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    preco: Optional[float] = Field(None, gt=0)
    quantidade: Optional[int] = Field(None, ge=0)
   
    @validator('preco')
    def preco_nao_pode_ser_zero(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v
   
    @validator('nome')
    def nome_nao_pode_ser_vazio(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Nome não pode ser vazio')
        return v


class ProdutoResponse(ProdutoBase):
    """Schema para LER produto"""
    id: int
    data_cadastro: datetime
   
    class Config:
        orm_mode = True