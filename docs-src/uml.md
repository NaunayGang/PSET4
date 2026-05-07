---
title: Diagramas UML - Diseño del Sistema IncidentFlow
---

## Visión General

Este documento contiene los diagramas PlantUML que visualizan la arquitectura del sistema IncidentFlow, modelo de dominio, flujos de trabajo y casos de uso. Estos diagramas son esenciales para entender el diseño del sistema y sirven como referencia para la implementación.

## Diagrama de Máquina de Estados

El diagrama de máquina de estados muestra el ciclo de vida de un incidente y todas las transiciones válidas entre estados.

![Diagrama de Máquina de Estados](../resources/images/IncidentFlowStateMachine.svg)

### Descripciones de Estados

-   **OPEN**: Estado inicial cuando se reporta un incidente
-   **TRIAGED**: El incidente ha sido evaluado por severidad e impacto
-   **ASSIGNED**: El incidente ha sido asignado a un respondedor técnico
-   **IN_PROGRESS**: El respondedor asignado está trabajando activamente en la solución
-   **RESOLVED**: La solución ha sido implementada pero aún no formalmente cerrada
-   **CLOSED**: El incidente está formalmente cerrado con resumen y auditoría completa
-   **ESCALATED**: Puede activarse desde cualquier estado; incidente escalado a un nivel superior
-   **CANCELLED**: El incidente fue una falsa alarma o ya no es relevante

### Transiciones Válidas

Desde **OPEN**:

-   → TRIAGED (después de evaluación)
-   → CANCELLED (si es falsa alarma)
-   → ESCALATED (si necesita escalamiento inmediato)

Desde **TRIAGED**:

-   → ASSIGNED (cuando se asigna el respondedor)
-   → CANCELLED (si se determina que no es urgente)
-   → ESCALATED (si se necesita escalamiento)

Desde **ASSIGNED**:

-   → IN_PROGRESS (cuando inicia el trabajo)
-   → CANCELLED (si no se necesita)
-   → ESCALATED (para escalar)

Desde **IN_PROGRESS**:

-   → RESOLVED (cuando se implementa la solución)
-   → ESCALATED (para escalar)

Desde **RESOLVED**:

-   → CLOSED (solo Commander/Admin puede cerrar; CRITICAL requiere resumen)
-   → IN_PROGRESS (si el problema reaparece)

Desde **ESCALATED**:

-   → ASSIGNED (reasignar y continuar)
-   → IN_PROGRESS (continuar desde escalamiento)

Desde **CANCELLED** o **CLOSED**:

-   → [Fin] (Estados terminales)

## Diagrama de Clases

El diagrama de clases muestra las entidades del dominio, sus atributos, relaciones e interfaces clave para el patrón repository.

![Diagrama de Clases](../resources/images/IncidentFlowClassDiagram.svg)

### Entidades Principales

**Usuario**

-   id: UUID
-   email: str
-   nombre: str
-   rol: Rol (Operator, Commander, Responder, Manager, Admin)
-   activo: bool
-   creado_en: DateTime

**Incidente** (Raíz de Agregado)

-   id: UUID
-   título: str
-   descripción: str
-   severidad: Severidad (LOW, MEDIUM, HIGH, CRITICAL)
-   estado: EstadoIncidente
-   creador_id: UUID (referencia a Usuario)
-   asignador_id: UUID (referencia a Usuario, nullable)
-   creado_en: DateTime
-   actualizado_en: DateTime
-   resuelto_en: DateTime (nullable)
-   cerrado_en: DateTime (nullable)
-   resumen_resolución: str (nullable)

Métodos clave:

-   `cambiar_estado(nuevo_estado, usuario)`: Cambia el estado del incidente con validación
-   `asignar(usuario, commander)`: Asigna el incidente a un usuario
-   `agregar_comentario(texto, usuario)`: Agrega un comentario al timeline
-   `cambiar_severidad(nueva_severidad, usuario)`: Cambia la severidad con auditoría
-   `puede_cerrar()`: Valida si el incidente puede cerrarse (CRITICAL requiere resumen)
-   `es_critical()`: Retorna true si la severidad es CRITICAL

**Comentario**

-   id: UUID
-   incidente_id: UUID (referencia a Incidente)
-   autor_id: UUID (referencia a Usuario)
-   texto: str
-   creado_en: DateTime

**LogAuditoría** (para cumplimiento y depuración)

-   id: UUID
-   incidente_id: UUID (referencia a Incidente)
-   usuario_id: UUID (referencia a Usuario)
-   acción: str (qué cambió: estado, severidad, asignación, etc)
-   valor_anterior: str (nullable)
-   valor_nuevo: str (nullable)
-   timestamp: DateTime
-   detalles: JSON (contexto adicional)

**Notificación**

-   id: UUID
-   usuario_id: UUID (referencia a Usuario)
-   incidente_id: UUID (referencia a Incidente)
-   tipo_evento: str (INCIDENTE_CREADO, SEVERIDAD_CAMBIADA, etc)
-   mensaje: str
-   leída: bool
-   created_at: DateTime

### Enumeraciones

**Severidad**

-   LOW
-   MEDIUM
-   HIGH
-   CRITICAL

**EstadoIncidente**

-   OPEN
-   TRIAGED
-   ASSIGNED
-   IN_PROGRESS
-   RESOLVED
-   CLOSED
-   ESCALATED
-   CANCELLED

**Rol**

-   OPERATOR
-   COMMANDER
-   RESPONDER
-   MANAGER
-   ADMIN

### Interfaces de Repository (Inversión de Dependencia)

Todas las implementaciones de la capa de infraestructura dependen de estas interfaces del dominio:

-   **IIncidentRepository**: Operaciones CRUD en incidentes, filtrado por estado/severidad/asignado
-   **ICommentRepository**: Crear y recuperar comentarios de incidentes
-   **IAuditLogRepository**: Crear y recuperar logs de auditoría
-   **IUserRepository**: Recuperar información de usuario por ID o email
-   **IEventBus**: Publicar eventos, suscribir a manejadores de eventos

## Diagrama de Secuencia: Flujo de Incidente CRITICAL

Este diagrama de secuencia ilustra el ciclo de vida completo de un incidente de severidad CRITICAL desde su creación hasta la resolución y cierre.

![Diagrama de Secuencia](../resources/images/IncidentFlowSequenceCritical.svg)

### Pasos del Flujo

1.  **Operador crea incidente CRITICAL** vía UI de Streamlit
2.  **Frontend envía solicitud POST /incidentes** a la API
3.  **Capa API valida** y rutea a la capa de Aplicación
4.  **Capa de Aplicación:**
   -   Valida datos del incidente
   -   Guarda en base de datos
   -   Publica evento INCIDENTE_CREADO
   -   Como severidad=CRITICAL, publica eventos de notificación
5.  **Event Bus notifica** a Commander y Manager inmediatamente (notificaciones en memoria)
6.  **Commander recibe notificación** y ve los detalles del incidente
7.  **Commander asigna** incidente a un Technical Responder y cambia estado a ASSIGNED
8.  **Sistema аудит** la asignación y publica evento INCIDENTE_ASIGNADO
9.  **Responder es notificado** de la asignación
10. **Responder inicia trabajo**, transiciona a IN_PROGRESS
11. **Responder agrega comentario** con detalles de investigación
12. **Responder resuelve** el incidente y transiciona a RESOLVED
13. **Sistema notifica** al Manager de la resolución
14. **Commander cierra** el incidente (solo Commander/Admin puede hacer esto para CRITICAL)
15. **Sistema valida** que el incidente CRITICAL tiene un resumen antes de permitir el cierre
16. **Sistema аудит** el cierre y publica evento INCIDENTE_CERRADO
17. **Estado final**: Incidente está CERRADO con timeline completo y auditoría

## Diagrama de Casos de Uso

El diagrama de casos de uso muestra qué acciones puede realizar cada rol en el sistema IncidentFlow.

![Diagrama de Casos de Uso](../resources/images/IncidentFlowUseCaseDiagram.svg)

### Capacidades por Rol

**Operador**

-   Crear Incidente
-   Agregar Comentario
-   Ver Incidente
-   Ver Dashboard (lista básica)

**Incident Commander** (Más Acciones)

-   Crear Incidente
-   Triar Incidente
-   Asignar Incidente
-   Agregar Comentario
-   Cambiar Estado (con restricciones)
-   Cambiar Severidad
-   Ver Incidente
-   Ver Dashboard (con enfoque en asignaciones y timeline)
-   Escalar Incidente
-   Cerrar Incidente (restringido: CRITICAL necesita resumen)

**Technical Responder**

-   Agregar Comentario
-   Cambiar Estado (limitado: puede mover a IN_PROGRESS, RESOLVED)
-   Ver Incidente
-   Ver Dashboard (sus incidentes asignados)

**Manager** (Solo Lectura + Auditoría)

-   Ver Incidente (solo lectura)
-   Ver Dashboard (métricas, distribución de incidentes, count sin asignar)
-   Ver Log de Auditoría (visibilidad completa para cumplimiento)

**Admin** (Acceso Completo)

-   Todas las acciones de todos los roles
-   Crear/Gestionar Usuarios
-   Reasignar Incidentes
-   Acceso Completo al Log de Auditoría

## Diagrama de Arquitectura Hexagonal

Este diagrama muestra cómo el sistema está organizado en una arquitectura hexagonal (clean) con clara separación de responsabilidades.

![Arquitectura Hexagonal](../resources/images/IncidentFlowArchitecture.svg)

### Capas Explicadas

#### Capa de Frontend

-   **UI Streamlit**: Interfaz multi-página para diferentes roles de usuario
-   Maneja lógica de presentación e interacción del usuario
-   Llama a endpoints de la API del Backend

#### Capa API

-   **Endpoints REST FastAPI**: Toda comunicación externa
-   Validación de solicitudes y serialización de respuestas
-   Decoradores de permisos para autorización

#### Capa de Aplicación

-   **Casos de Uso**: Operaciones de negocio (CrearIncidente, TriarIncidente, etc)
-   Orquesta entidades del dominio y servicios de infraestructura
-   No hay llamadas directas a base de datos; depende de interfaces de repository
-   DTOs validan entrada y dan forma a la salida

#### Capa de Dominio (Core - Sin Dependencias Externas)

-   **Entidades**: Objetos de negocio con identidad (Incidente, Usuario, Comentario)
-   **Objetos de Valor**: Enumeraciones (Severidad, EstadoIncidente, Rol)
-   **Reglas de Negocio**: Máquina de estados, restricciones CRITICAL, permisos
-   **Abstracciones (Interfaces)**: IIncidentRepository, IEventBus, etc
-   **Esta capa es testeable en aislamiento** sin mocks

#### Capa de Infraestructura

-   **Repositories**: Implementaciones concretas de interfaces del dominio
-   **Base de Datos**: PostgreSQL con ORM SQLAlchemy y migraciones Alembic
-   **Event Bus**: Publicar/suscribir en memoria para eventos y notificaciones
-   Depende de abstracciones del dominio (principio de inversión de dependencia)

### Principios Arquitectónicos Clave

1.  **Inversión de Dependencia**: Módulos de alto nivel no dependen de módulos de bajo nivel; ambos dependen de abstracciones
2.  **Responsabilidad Única**: Cada capa tiene una razón para cambiar
3.  **Testabilidad**: Capa de dominio es testeable sin test doubles
4.  **Flexibilidad**: Fácil cambiar implementaciones (ej: diferente base de datos, event bus)

## Generación de Diagramas

Todos los diagramas se generan desde archivos fuente PlantUML (.puml) y se compilan a PNG usando:

```bash
nix shell nixpkgs#plantuml --command plantuml -o docs-src/resources/images docs-src/uml/*.puml
```

O vía el método de compilación documentado:

```bash
nix develop path:. --command tern-core
```

## Próximos Pasos

Estos diagramas deben guiar:

-   Implementación de la capa de dominio y repositories del backend
-   Diseño de UI y flujo de trabajo del frontend
-   Diseño y validación de endpoints de API
-   Diseño de casos de prueba y fixtures de testing
-   Discusiones de equipo y code reviews