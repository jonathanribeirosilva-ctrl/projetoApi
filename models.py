from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime


class Produto(Base):
    """Modelo de Produto - Representa um produto na mercearia"""
   
    # Nome da tabela no banco
    __tablename__ = "produtos"
   
    # Colunas da tabela (campos da ficha)
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)  # Não pode ser vazio
    preco = Column(Float, nullable=False)       # Preço em reais
    quantidade = Column(Integer, nullable=False, default=0)
    data_cadastro = Column(DateTime, default=datetime.now)
   
    def __repr__(self):
        """Como o produto aparece quando printado"""
        return f"<Produto {self.nome} - R${self.preco}>"
