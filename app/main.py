from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings

docs_kwargs = {}
if settings.ENV.lower() == "production":
    docs_kwargs = {"docs_url": None, "redoc_url": None, "openapi_url": "/openapi.json"}

app = FastAPI(**docs_kwargs)

# Configure CORS for both local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://www.zepedrocmota.com",  # Personal portfolio domain
        "https://whatevs-zepedrocm.vercel.app",  # Whatevs app domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"ok": True}

# Routers
from .features.contact.router import router as contact_router  # noqa: E402
from .features.debate.router import router as debate_router  # noqa: E402

app.include_router(contact_router)
app.include_router(debate_router)