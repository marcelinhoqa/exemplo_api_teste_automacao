from fastapi import FastAPI, HTTPException, Header
from models.user import User
from models.user_dto import UserDto
from services.user_db import UserDb
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Adicionando middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP, como GET, POST, PUT, DELETE
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

user_db = UserDb()

@app.post("/user/")
def create_user(user: User):
    try:
        user_db.insert(user)
        return {"message": "Usuário criado com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  # Aqui, você pode passar o erro diretamente no detail.

@app.get("/user/", response_model=User)
async def get_user_by_email_header(email: str = Header(...)):
    try:
        print(f"Recebendo e-mail do cabeçalho: {email}")  # Imprime o e-mail recebido no cabeçalho
        user = user_db.find_by_email(email)
        
        if user:
            print(f"Usuário encontrado: {user}")  # Se encontrar, imprime os dados do usuário
            return user
        else:
            print("Usuário não encontrado.")  # Se não encontrar, imprime uma mensagem
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  # Passa a mensagem de erro como o detail

@app.put("/user/{user_id}")
async def update_user(user_id: int, user: User):
    try:
        user_db.update(user_id, user)
        return {"message": f"Usuário com ID {user_id} atualizado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    try:
        user_db.delete(user_id)
        return {"message": f"Usuário com ID {user_id} foi deletado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/users/", response_model=list[UserDto])
async def get_all_users():
    try:
        users = user_db.get_all()
        return users
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Erro ao buscar os usuários.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
