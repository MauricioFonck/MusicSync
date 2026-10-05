# Estructura del repositorio

```text
musicsync/
├── backend/
│   ├── src/musicsync/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── services/
│   │   │   ├── events/
│   │   │   └── ports/
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   ├── dto/
│   │   │   └── services/
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   ├── downloaders/
│   │   │   ├── media/
│   │   │   ├── storage/
│   │   │   ├── filesystem/
│   │   │   └── configuration/
│   │   └── adapters/
│   │       ├── api/
│   │       ├── websocket/
│   │       └── cli/
│   └── tests/
├── frontend/
│   └── src/app/
├── docs/
├── scripts/
├── .env.example
├── docker-compose.yml
└── README.md
```
