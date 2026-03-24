from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine


# Criar as tabelas no banco
models.Base.metadata.create_all(bind=engine)


# Criar a aplicação FastAPI
app = FastAPI(
    title="API da Mercearia do João",
    description="Sistema completo para controlar produtos da mercearia",
    version="2.0.0"  # Atualizamos a versão!
)


# Dependência para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== ENDPOINTS EXISTENTES ====================


@app.get("/")
def home():
    """Página inicial - Agora com mais opções!"""
    return {
        "mensagem": "Bem-vindo à API da Mercearia do João! ",
        "endpoints_disponiveis": {
            "GET /produtos": "Listar todos os produtos",
            "GET /produtos/{id}": "Buscar um produto específico",
            "GET /produtos/busca/{nome}": "Buscar produtos por nome",
            "POST /produtos": "Cadastrar um novo produto",
            "PUT /produtos/{id}": "ATUALIZAR um produto existente  NOVO",
            "DELETE /produtos/{id}": "REMOVER um produto  NOVO"
        }
    }


@app.post("/produtos", response_model=schemas.ProdutoResponse, status_code=201)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    """POST - Cadastrar um novo produto"""
    db_produto = models.Produto(
        nome=produto.nome,
        preco=produto.preco,
        quantidade=produto.quantidade
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@app.get("/produtos", response_model=List[schemas.ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    """GET - Listar todos os produtos"""
    return db.query(models.Produto).all()


@app.get("/produtos/{produto_id}", response_model=schemas.ProdutoResponse)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    """GET - Buscar um produto pelo ID"""
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado!")
    return produto


@app.get("/produtos/busca/{nome}")
def buscar_por_nome(nome: str, db: Session = Depends(get_db)):
    """GET - Buscar produtos por nome"""
    produtos = db.query(models.Produto).filter(
        models.Produto.nome.ilike(f"%{nome}%")
    ).all()
    return produtos


# ==================== NOVOS ENDPOINTS - PUT E DELETE ====================


@app.put("/produtos/{produto_id}", response_model=schemas.ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto_update: schemas.ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """
    PUT - ATUALIZAR um produto existente 
   
    Exemplo de uso:
    {
        "preco": 28.90,
        "quantidade": 20
    }
   
    Ou para atualizar tudo:
    {
        "nome": "Arroz Parboilizado 5kg",
        "preco": 32.50,
        "quantidade": 15
    }
    """
   
    # 1º Passo: Procurar o produto no banco
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
   
    # 2º Passo: Verificar se o produto existe
    if not produto:
        raise HTTPException(
            status_code=404,
            detail=f"Produto com ID {produto_id} não encontrado! "
        )
   
    # 3º Passo: Atualizar APENAS os campos que foram enviados
    # O método dict() transforma nosso schema em dicionário
    # exclude_unset=True ignora campos que não foram enviados
    update_data = produto_update.dict(exclude_unset=True)
   
    print(f" Atualizando produto {produto_id} com: {update_data}")
   
    # 4º Passo: Aplicar as mudanças
    for campo, valor in update_data.items():
        setattr(produto, campo, valor)
   
    # 5º Passo: Salvar no banco
    db.commit()
    db.refresh(produto)
   
    # 6º Passo: Retornar o produto atualizado
    return produto




@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """
    DELETE - REMOVER um produto do sistema 
   
    Cuidado: Esta operação NÃO TEM VOLTA!
    Uma vez deletado, o produto some do banco.
    """
   
    # 1º Passo: Procurar o produto
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
   
    # 2º Passo: Verificar se existe
    if not produto:
        raise HTTPException(
            status_code=404,
            detail=f"Produto com ID {produto_id} não encontrado! Não dá pra deletar o que não existe."
        )
   
    # 3º Passo: Guardar informações para a mensagem de confirmação
    nome_produto = produto.nome
   
    # 4º Passo: DELETAR o produto (é sério, não tem volta!)
    db.delete(produto)
    db.commit()
   
    # 5º Passo: Retornar mensagem de sucesso
    return {
        "mensagem": f" Produto '{nome_produto}' (ID: {produto_id}) foi removido com sucesso!",
        "detalhes": "Operação de DELETE concluída. O produto não está mais no sistema."
    }




# ==================== ENDPOINTS EXTRAS (DESAFIOS) ====================


@app.delete("/produtos")
def deletar_todos_produtos(db: Session = Depends(get_db)):
    """
    DELETE - REMOVER TODOS os produtos (USE COM CUIDADO!)
   
    Este endpoint é como um "botão de emergência" - apaga tudo!
    """
    # Contar quantos produtos existem
    quantidade = db.query(models.Produto).count()
   
    if quantidade == 0:
        return {"mensagem": "Não há produtos para deletar. Banco já está vazio!"}
   
    # Deletar todos
    db.query(models.Produto).delete()
    db.commit()
   
    return {
        "mensagem": f" {quantidade} produtos foram removidos do sistema!",
        "atencao": "Esta operação não pode ser desfeita. Todos os produtos foram deletados."
    }




@app.put("/produtos/{produto_id}/aumentar/{quantidade}")
def aumentar_estoque(produto_id: int, quantidade: int, db: Session = Depends(get_db)):
    """
    PUT - Endpoint especial para AUMENTAR o estoque
    Exemplo: /produtos/1/aumentar/10  (aumenta 10 unidades no estoque)
    """
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser positiva!")
   
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado!")
   
    produto.quantidade += quantidade
    db.commit()
    db.refresh(produto)
   
    return {
        "mensagem": f" Estoque aumentado em {quantidade} unidades!",
        "produto": produto.nome,
        "estoque_atual": produto.quantidade
    }
