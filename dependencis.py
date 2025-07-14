from fastapi import Depends, HTTPException
from main import ALGORITHM, SECRET_KEY, oauth2_chema
from models import Usuario, db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError
from main import oauth2_chema



def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    
    finally:
        session.close()


#criar token
def verificar_token(token: str = Depends(oauth2_chema), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="acesso Negado verifica a data do token")
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="acesso invalido")
    return usuario