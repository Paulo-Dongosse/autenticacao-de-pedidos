from fastapi import APIRouter, Depends, HTTPException
from dependencis import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema
from sqlalchemy.orm import Session
from models import Pedido, Usuario, ItemPedido


order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedido():
    """
    Todads as rotas precisão de autenticação
    """
    return {"mensaguens": " vc acessou a rota pedido"}


@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    """
    Aqui vc vai criar o pedido. OBS: precisa logar primeiro e passa o id do usuario,
      so o usuario e o admin têm esta privilegio
    """
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"pedido criado com Sucesso: {novo_pedido.id}"}


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Aqui vc vai cancelar o pedido. OBS: precisa logar primeiro e passa o id do usuario
    só o usuario e o admin têm esta privilegio
    """

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not Pedido:
        raise HTTPException(status_code=400, detail="pedido nao encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="vc nao tem autorizacao pra cancelar esse pedido")
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": f"Pedido numero {pedido.id} cancelado com sucesso",
        "pedido": pedido
}

@order_router.get("/listar")
async def listar_pedido(session: Session= Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Aqui vc vai listar o pedido. OBS: precisa logar primeiro e passa o id do usuario
    só o usuario e o admin têm esta privilegio
    """
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="vc nao tem autorizacao de fazer esta operacao")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
        }


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,
                                item_pedido_schema: ItemPedidoSchema,
                                session: Session = Depends(pegar_sessao),
                                  usuario: Usuario = Depends(verificar_token)):
    """
    Aqui vc vai adicionar item ao pedido. OBS: segue as lacunas
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, datail="Pedido nao existe na base de dados")
    
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="vc nao tem autorizacao de fazer esta operacao")
    
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho,
                             item_pedido_schema.preco_unitario, id_pedido)
    
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }


@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,
                                session: Session = Depends(pegar_sessao),
                                  usuario: Usuario = Depends(verificar_token)):
    """
    Aqui vc vai remover o pedido. OBS: precisa logar primeiro, preencha as lacunas
    """
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, datail="O item noPedido nao existe na base de dados")
    
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="vc nao tem autorizacao de fazer esta operacao")
    
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def Finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Aqui vc vai finalizar o pedido. OBS: precisa logar primeiro e prencher as lacunas
    """

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not Pedido:
        raise HTTPException(status_code=400, detail="pedido nao encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="vc nao tem autorizacao pra FINALIZAR esse pedido")
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": f"Pedido numero {pedido.id} finalizado com sucesso",
        "pedido": pedido
}


#vIZUALIZAR 1 pedido
@order_router.get("/pedido/{id_pedido}")
async def vizualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
     Só o usuario e o Admin têm esse privilegio
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not Pedido:
        raise HTTPException(status_code=400, detail="pedido nao encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="vc nao tem autorizacao pra FINALIZAR esse pedido")
    return{
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

    #vIZUALIZAR todos os pedido
@order_router.get("/listar/pedido-usuario")
async def listar_pedido(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
     Só o usuario e o Admin têm esse privilegio
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
    return{
        "pedidos": pedidos
    }
