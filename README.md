# IncidentFlow

**Sistema de escalamiento centralizado para incidentes operativos críticos**

## Caso de Negocio

La empresa opera servicios críticos donde incidentes (pagos fallidos, integraciones caídas, alertas de seguridad) requieren coordinación inmediata. Actualmente, los equipos se coordinan por chats dispersos, lo que genera pérdida de contexto, responsables poco claros y poca visibilidad.

**IncidentFlow** centraliza la gestión de incidentes con responsables claramente asignados, estados bien definidos, timeline confiable y notificaciones inmediatas para casos críticos.

## Integrantes

- **@nikotov** - Backend (Python, FastAPI, Clean Architecture)
- **@FelipeBhrqz** - Frontend (Streamlit)
- **@Nicothekiller** - DevOps (Docker, GitHub Actions, Render)
- **@yuuhikaze** - Documentación, UML, Tests (PlantUML, pytest)

## Descripción del Problema

Durante un incidente no queda claro:
- Quién está a cargo
- Qué severidad tiene
- Qué acciones se tomaron
- Quién fue notificado
- Si el incidente está resuelto
- Qué se aprendió al final

## Stack Técnico

| Componente | Tecnología |
|------------|-----------|
| **Backend** | FastAPI (Python) |
| **Frontend** | Streamlit |
| **Base de Datos** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Arquitectura** | Hexagonal |
| **Contenedores** | Docker Compose |
| **CI/CD** | GitHub Actions |
| **Deploy** | Render (dev/prod) |

## Arquitectura Propuesta

La solución sigue **Arquitectura Hexagonal** en 4 capas:

```
┌─────────────────────────────────────────┐
│           Frontend (Streamlit)          │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────┴───────────────────┐
│              API Layer (FastAPI)         │
├─────────────────────────────────────────┤
│          Application Layer               │
│     (Use Cases, Service Orchestration)   │
├─────────────────────────────────────────┤
│            Domain Layer                  │
│  (Entities, Value Objects, Rules)        │
├─────────────────────────────────────────┤
│         Infrastructure Layer             │
│    (DB, Repositories, Event Bus)         │
└─────────────────────────────────────────┘
```

## Descripción del Flujo

### Estados Principales
```
OPEN → TRIAGED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
```

### Roles y Permisos

| Rol | Crear | Asignar | Cambiar Estado | Comentar | Leer | Auditar |
|-----|-------|---------|----------------|----------|------|---------|
| Operator | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Commander | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Responder | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Manager | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Reglas Críticas

- Incidentes **CRITICAL** notifican inmediatamente a Commander y Manager
- **CRITICAL** no puede cerrarse sin resumen de resolución
- No se puede pasar a **IN_PROGRESS** sin responsable asignado
- Una vez **CLOSED**, un incidente no vuelve a **IN_PROGRESS**
- Cambios de severidad deben auditarse
- Solo Commander/Admin pueden resolver o cerrar incidentes

## Interfaces de Usuario

### Lista Principal de Incidentes
![Incident List](docs-src/resources/images/incident-list-main-page.jpeg)

### Formulario de Creación
![Create Incident](docs-src/resources/images/create-new-incident-form.jpeg)

### Detalle e Historial
![Incident Detail](docs-src/resources/images/incident-detail-and-timeline.jpeg)

### Filtros y Paginación
![Incident List Filters](docs-src/resources/images/incident-list-with-filters-and-pagination.jpeg)

### Dashboard de Manager
![Manager Dashboard](docs-src/resources/images/manager-dashboard-reduced-view.jpeg)

### Dashboard de Admin
![Admin Dashboard](docs-src/resources/images/admin-dashboard.jpeg)

## Cómo Correr Localmente

### Requisitos Previos

**Nix (para reproducibilidad):**
- Linux/macOS/Windows (WSL2)
- Instala Nix desde: https://nixos.org/download/

Si no tienes Nix, necesitas:
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (opcional, para frontend tools)

### Con Docker Compose (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/NaunayGang/PSET4.git
cd PSET4

# Levantar stack completo
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:8501
# PostgreSQL: localhost:5432
```

### Sin Docker (Desarrollo Local)

```bash
# Entrar al entorno Nix
nix develop

# Backend
cd backend
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:password@localhost:5432/incidentflow"
uvicorn app.api.main:app --reload

# Frontend (en otra terminal)
cd frontend
streamlit run app/main.py
```

## Cómo Correr Docker Compose

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Apagar servicios
docker-compose down

# Reconstruir imágenes
docker-compose up -d --build
```

## Flujo de GitHub Actions

### En branch `dev`
Cuando hay push a `dev`:
1. Instalar dependencias
2. Lint (flake8/ruff)
3. Tests (pytest)
4. Build Docker backend
5. Push a Docker Hub con tag `dev`
6. Deploy automático a Render dev environment

### En branch `main`
Cuando hay push a `main` (solo mediante merge de PR):
1. Todas las validaciones de `dev`
2. Build Docker con tag `latest` y `prod`
3. Push a Docker Hub
4. Deploy automático a Render prod environment

**Nota**: No se acepta deploy directo a producción desde branches feature.

## Documentación

La documentación está ubicada en `/docs-src/` y se compila a HTML.

### Compilar Documentación

```bash
nix develop path:. --command tern-core
```

Esto genera archivos HTML en la carpeta `docs/`.

### Servir Documentación Localmente

Sirve la documentación compilada (HTML) con:

```bash
nix develop 'path:.#resources' --command miniserve --color-scheme monokai docs
```

Luego abre tu navegador en: http://localhost:8080

### Secciones de Documentación

- **discovery.md**: Descubrimiento de requerimientos, contexto del negocio, reglas
- **requirements.md**: Requerimientos funcionales y no funcionales
- **uml/**: Diagramas (State Machine, Class, Sequence, Use Cases)
- **API Reference**: Documentación de endpoints (generada a partir de docstrings)

## Nix

Nix es un gestor de paquetes declarativo que asegura reproducibilidad.

### Obtener Nix

Nix está disponible para todas las plataformas. Visita: https://nixos.org/download/

Soportado en:
- **Linux**: NixOS, Ubuntu, Fedora, Debian, Arch, y más
- **macOS**: Intel y Apple Silicon
- **Windows**: WSL2 (con Nix instalado en el subsistema)

Sigue las instrucciones del sitio oficial para tu plataforma específica.

## GitHub Project & Issues

El proyecto usa GitHub Project con columnas:
- **Backlog**: Issues sin asignar o no priorizadas
- **Todo**: Listas de trabajos por hacer
- **In Progress**: Trabajo actual
- **In Review**: En revisión (PR abierta)
- **Done**: Completado

Cada issue es una historia de usuario en formato:
> Como [rol], quiero [acción], para [beneficio].

## Environment Setup

1. Copy the template and create your local env file:

```bash
cp .env.example .env
```

2. Edit `.env` and set your local values. At minimum:

```env
DATABASE_URL=postgresql://app_user:YOUR_PASSWORD@localhost:5432/incident_flow_db
```

3. Run Alembic commands with this project's `DATABASE_URL`:

```bash
export DATABASE_URL=postgresql://app_user:YOUR_PASSWORD@localhost:5432/incident_flow_db
alembic current
alembic heads
alembic upgrade head
```

Notes:
- Do not commit `.env`.
- Commit `.env.example` only.
- Keep one dedicated database per project to avoid migration conflicts.

## Links a Render

- **Dev**: https://incidentflow-dev.onrender.com (auto-deploya desde `dev`)
- **Prod**: https://incidentflow-prod.onrender.com (auto-deploya desde `main`)

## Contributing

1. Crea un branch con el nombre del issue: `git checkout -b issue-#123`
2. Haz commits descriptivos siguiendo Angular style: `feat:`, `fix:`, `docs:`, etc.
3. Sube cambios y crea una PR
4. Asegúrate que GitHub Actions pase
5. Solicita review de compañeros
6. Una vez aprobada, mergea a `dev` primero, luego a `main`

## Próximas Fases

- **PSet #4 (Actual)**: Discovery, requisitos, setup DevOps, UML inicial
- **Proyecto Final**: Implementación completa del MVP

## Licencia

Proyecto académico - USFQ Systems Design