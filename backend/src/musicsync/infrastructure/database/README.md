# Persistencia

La infraestructura usa SQLAlchemy 2 sobre SQLite en el MVP. Los modelos ORM viven aquí y no se importan desde `domain/`.

## Desarrollo

```bash
uv run alembic upgrade head
uv run alembic downgrade base
```

El repositorio traduce entidades y value objects a filas SQL y viceversa. Las migraciones versionadas son la fuente de cambios de esquema; `Base.metadata.create_all` se reserva para pruebas aisladas.
