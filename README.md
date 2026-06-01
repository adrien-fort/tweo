# TWEO

Group activity organiser — helps groups vote and decide on shared activities (movies, games, board games, role play, etc.).

## Stack

- **Backend**: Python (SOLID, OOP, TDD)
- **Frontend**: TBD (React candidate)

## Structure

```
tweo/
├── backend/
│   ├── app/
│   │   ├── api/              # HTTP layer — routes and controllers
│   │   ├── core/
│   │   │   ├── domain/       # Entities and value objects
│   │   │   ├── interfaces/   # Abstract interfaces (Dependency Inversion)
│   │   │   └── services/     # Business logic and use cases
│   │   └── infrastructure/   # DB, external service adapters
│   └── tests/
│       ├── unit/
│       └── integration/
├── frontend/                 # TBD
└── docs/
```

## Principles

- **SOLID** — each module has a single responsibility; dependencies point inward via interfaces
- **OOP** — domain modelled as entities and value objects
- **TDD** — tests written before implementation
