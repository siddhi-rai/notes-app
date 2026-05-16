import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routes import users, notes, about

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes App API",
    description="A multi-user notes service with REST APIs for managing personal notes.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, tags=["Authentication"])
app.include_router(notes.router, tags=["Notes"])
app.include_router(about.router, tags=["About"])


# OpenAPI JSON endpoint
@app.get("/openapi.json", include_in_schema=False)
def get_openapi():
    return JSONResponse(content=app.openapi())


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Notes App API. Visit /docs for interactive documentation."}
