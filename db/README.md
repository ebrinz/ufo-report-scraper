

## Initialization

Before proceeding, ensure that Docker is installed and running on your system.

For installation instructions, visit the [Docker documentation](https://docs.docker.com/get-docker/).

```bash
docker-compose up --build -d
```

```bash
docker exec -it postgres_vector psql -U local -d postgres -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

