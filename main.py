from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES"))



app = FastAPI(title="Autenticação De Pedidos", description="API para Atutenticção de usuario e Cerenciamento de Pedidos",)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
oauth2_chema = OAuth2PasswordBearer(tokenUrl="/auth/login-form")



from auth_routes import auth_router
from order_routes import order_router


app.include_router(auth_router)
app.include_router(order_router)

# uvicorn main:app --reload

#
#ordens
# rest API

# get  -> leitura/pegar
# post -> enviar/criar
# put/patch -. editar
# delete -> deletar