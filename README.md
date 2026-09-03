# Project Management MVP

## Part 2: Run the scaffold

Prerequisites:

- Docker Desktop or Docker Engine with Compose
- `uv` for local backend development

Start the container:

```sh
./scripts/start-linux.sh
```

Use `./scripts/start-mac.sh` on macOS or `scripts\\start-windows.bat` on Windows. The application is available at `http://localhost:8000/` and the health endpoint is `http://localhost:8000/api/health`.

Stop the container:

```sh
./scripts/stop-linux.sh
```

Use the matching macOS or Windows stop script on those platforms. Compose stores application data in its named volume for later database phases.

## Backend tests

```sh
cd backend
uv run pytest
```

The root `.env` file is optional for the scaffold and is ignored by Git. Later AI phases will use its `OPENROUTER_API_KEY` value server-side.
