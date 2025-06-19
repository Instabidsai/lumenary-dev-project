# Solar App Template

This repository contains a minimal example of a Solar application consisting of a React frontend and several Python services. It is intended as a starting point for new projects and includes the following packages:

- **app** – React application built with Vite.
- **services** – FastAPI backend exposing a small API.
- **logging-server** – simple FastAPI server for websocket logging.

## Getting Started

1. Install Node and Python dependencies.
   ```bash
   cd app && pnpm install
   cd ../services && pip install -e .[dev]
   ```
2. Copy `.env.example` to `.env` and update values as needed.
3. Run the backend services:
   ```bash
   cd services
   uvicorn main:app --reload
   ```
4. Start the frontend:
   ```bash
   cd ../app
   pnpm dev
   ```

## Development

- `pnpm test` – runs frontend unit tests with Vitest.
- `pytest` – runs Python unit tests.

See the individual service READMEs for more details.

