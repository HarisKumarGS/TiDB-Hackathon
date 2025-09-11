from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.insights import router as insights_router
from src.app.api.simulation import router as simulation_router
from src.app.api.repository import router as repository_router
from src.app.api.status import router as status_router

app = FastAPI(
    title="Crash Lens API",
    description="API for crash analysis and insights",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(insights_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")
app.include_router(repository_router, prefix="/api/v1")
app.include_router(status_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"Hello": "World", "message": "Crash Lens API is running"}
