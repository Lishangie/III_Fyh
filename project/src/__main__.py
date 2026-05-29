"""Entry point for the Credit Risk Scoring service.

Run the FastAPI application using uvicorn with settings from the config.
"""

import uvicorn

from src.config import load_config


def main():
    """Start the Credit Risk Scoring API server."""
    config = load_config()
    uvicorn.run(
        "src.service.app:app",
        host=config.service.host,
        port=config.service.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
