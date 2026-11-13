from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_router
from app.deps import rate_limit

app = FastAPI(title="SiteCare AI - Website Maintenance Lead Finder", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    rate_limit(request)
    return await call_next(request)


app.include_router(api_router)


@app.get("/")
def root():
    return {"name": "SiteCare AI", "version": "1.0.0", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
