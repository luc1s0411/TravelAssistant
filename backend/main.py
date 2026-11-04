"""Run the development API directly from an IDE or the command line."""

from pathlib import Path

import uvicorn


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        app_dir=str(Path(__file__).resolve().parent),
    )


if __name__ == "__main__":
    main()
