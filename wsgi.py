"""
WSGI/ASGI adapter for Talisik Short URL FastAPI application.
Entrypoint used by gunicorn/uvicorn on any container-based host (e.g. Dokploy).
"""

from api.main import app

# For ASGI deployment (preferred for FastAPI)
application = app

# Alternative WSGI adapter if needed
def create_app():
    """Factory function to create the app instance"""
    return app

# For gunicorn with uvicorn workers
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 