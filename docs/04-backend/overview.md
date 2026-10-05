# Backend

## Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- Pytest
- Ruff
- MyPy

## Capas

### Domain
Reglas y modelos de negocio.

### Application
Casos de uso y orquestación.

### Infrastructure
Bases de datos, filesystem, USB, motores externos.

### Adapters
HTTP, WebSocket y CLI.

## Regla

FastAPI no debe llamar directamente a yt-dlp ni a SQLAlchemy desde los endpoints. Los endpoints llaman casos de uso.
