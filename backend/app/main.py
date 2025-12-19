"""FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import upload, analysis, export

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Visual tool for analyzing contraídos and other accounting documents",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix=settings.api_prefix)
app.include_router(analysis.router, prefix=settings.api_prefix)
app.include_router(export.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print(f"📊 API Documentation: http://localhost:8000/api/docs")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📤 Export directory: {settings.export_dir}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)
