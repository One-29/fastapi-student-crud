from fastapi import FastAPI

from routers import auth, chat, users

app = FastAPI(title="Realtime Chat API")

app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(users.router)
