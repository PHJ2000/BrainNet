from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, users, projects, nodes, tags, votes, ws

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brainstorming Collaboration API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(nodes.router)
app.include_router(tags.router)
app.include_router(votes.router)
app.include_router(ws.router)
