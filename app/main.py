from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health_router, summary_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    print(f"Starting Clinical Summary API")
    print(f"FHIR Server: {settings.fhir_base_url}")
    print(f"LLM Model: {settings.openai_model}")
    yield
    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Clinical Summary API",
        description=(
            "Generate comprehensive clinical patient summaries from FHIR R4 data "
            "using LLM-powered analysis. Queries patient demographics, conditions, "
            "medications, observations, and allergies from a FHIR server and produces "
            "structured clinical narratives."
        ),
        version="1.0.0",
        lifespan=lifespan,
        debug=settings.debug,
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
    app.include_router(health_router)
    app.include_router(summary_router)

    return app


app = create_app()
