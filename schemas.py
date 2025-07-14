from pydantic import BaseModel
from typing import Optional

class usuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class config:
        from_attributes =True

class PedidoSchema(BaseModel):
    usuario: int

    class config:
        from_attributes = True

class loginSchema(BaseModel):
    email: str
    senha: str
    
    class config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

    class config:
        from_attributes = True