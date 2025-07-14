from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencis import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_MINUTES, SECRET_KEY
from schemas import usuarioSchema, loginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime,timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario):
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    dic_info = {"sub": str(id_usuario), "espira": int(data_expiracao.timestamp())}
    jwt_codi = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
   
    return jwt_codi

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    
    return usuario


@auth_router.get("/")
async def autenticar():
    """
    rota padrao de autentificacao do sistema
    """
    return {"mensaguem": "vc acessou o padrao autenticado"}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: usuarioSchema, session: Session = Depends(pegar_sessao)):
    """
    Criar conta o cadastrar cliente, precisa informar false se o usuario nao for adiministador
    """
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    
    if usuario:
        return HTTPException(status_code=40, detail="Email do usuario ja Existe")
    else:
        senha_criptografada =  bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem:", f" usuario cadastrado com sucesso {usuario_schema.email}"}


    
#login
@auth_router.post("/login")
async def login(login_schema: loginSchema, session: Session = Depends(pegar_sessao)):
    """
    Esta funcao esta desabilitada, para o login usa o Authorize acima
    """
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario nao encontrado ou credencial invalida")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(day=7))
        return {"access_token": access_token,
                "user_refresh_token": refresh_token,
                 "token_type": "Bearer"
                 }


@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario nao encontrado ou credencial invalida")
    else:
        access_token = criar_token(usuario.id)
        return {"access_token": access_token,
                 "token_type": "Bearer"
                 }


@auth_router.get("/refresh")
async def user_refresh_token(usuario: Usuario = Depends(verificar_token)):
    """
    É precisa esta Autenticado pra ver a referencia
    """ 
    access_token = criar_token(usuario.id)
    return {"access_token": access_token,
                 "token_type": "Bearer"
                 }