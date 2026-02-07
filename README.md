Repositório do curso de FastAPI com Dunossauro.

Exemplo de `.env`:

```env
DATABASE_URL=postgresql+psycopg://user:password@127.0.0.1:5432/database
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Docker configuration for Testcontainers using MacOS + podman
# DOCKER_HOST=unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')
DOCKER_HOST=unix://<output-terminal>
TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
TESTCONTAINERS_RYUK_DISABLED=true
```