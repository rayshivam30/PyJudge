# Deployment Guide

## Compose Deployment

1. Create an environment file.

```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and replace `SECRET_KEY` with a long random value.

3. Start the stack.

```powershell
docker compose --env-file .env up --build -d
```

4. Verify health.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Environment Variables

| Variable | Purpose | Example |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL | `postgresql+psycopg://pyjudge:pyjudge@db:5432/pyjudge` |
| `REDIS_URL` | Celery broker/result backend | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing secret | `replace-with-random-secret` |
| `EXECUTOR_USE_DOCKER` | Enables Docker sandbox execution | `true` |
| `EXECUTOR_WORKSPACE_ROOT` | Temporary execution workspace | `/tmp/pyjudge` |

## Production Checklist

- Use managed PostgreSQL or persistent encrypted volumes.
- Rotate `SECRET_KEY` through a secret manager.
- Put the API behind TLS and a reverse proxy.
- Add request rate limiting at the proxy or API layer.
- Run Celery workers separately from the public API hosts.
- Restrict Docker socket access to worker hosts only.
- Prefer rootless Docker or a hardened container runtime.
- Add seccomp/AppArmor profiles for execution containers.
- Disable outbound network access for judge containers.
- Ship logs to a central log store.
- Add metrics for queue depth, job duration, verdict distribution, and worker failures.
- Replace startup `create_all` with Alembic migrations before schema changes in production.

## Scaling

Scale API and worker services independently:

```powershell
docker compose up --scale api=2 --scale worker=4 -d
```

Use a load balancer in front of API replicas. Increase worker count based on Redis queue depth and CPU availability.

## Database Migrations

The scaffold currently creates tables at startup for development convenience. For production, add Alembic migrations and run them during release:

```powershell
alembic upgrade head
```

## Backup and Recovery

- Schedule PostgreSQL backups.
- Test restore procedures.
- Keep submission source code retention aligned with your privacy policy.
- Separate backup access from runtime service credentials.