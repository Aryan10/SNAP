from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.routes import auth_routes, user_routes, feed_routes

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(feed_routes.router)
