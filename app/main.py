import logging
import time
from fastapi import FastAPI, Request
from app.routers import (
    auth_router,
    users_router,
    skills_router,
    profiles_router,
    jobs_router,
    proposals_router,
    contracts_router,
    milestones_router,
    reviews_router
)
from app.exceptions.custom_exceptions import StockFlowException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Freelancer Marketplace",
    description="Freelancer Marketplace Backend",
    version="1.0.0",
)

@app.exception_handler(StockFlowException)
async def stockflow_exception_handler(request: Request, exc: StockFlowException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(skills_router)
app.include_router(profiles_router)
app.include_router(jobs_router)
app.include_router(proposals_router)
app.include_router(contracts_router)
app.include_router(milestones_router)
app.include_router(reviews_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "Freelancer Marketplace"}