# wilkins-dashboard

## Installation

1. Copy .env to .env.local
2. Edit .env.local, for example:
```
# Postgres Settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wilkins

# App Settings
DATABASE_URL="postgresql+psycopg2://postgres:postgres@db:5432/wilkins"
``` 
3. make dev

Test the api at http://localhost:3000/docs