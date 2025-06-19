# Services

This package exposes a small FastAPI application used by the Solar example.

## Running

Install dependencies and run the server:

```bash
pip install -e .[dev]
uvicorn main:app --reload
```

Unit tests are located under `services/tests` and can be run with `pytest`.

