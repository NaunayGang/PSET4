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

-   → CLOSED (después de revisión formal)
-   → ESCALATED (si hay problemas)

Desde **ESCALATED**:

-   → ASSIGNED (reasignado a nivel superior)
-   → CANCELLED (si se determina que no es necesario)

Desde cualquier estado:

-   → CANCELLED (en cualquier momento)
-   → ESCALATED (en cualquier momento)

## Diagrama de Casos de Uso

El diagrama de casos de uso muestra las interacciones entre los actores y el sistema.

![Diagrama de Casos de Uso](../resources/images/IncidentFlowUseCases.svg)

### Actores

-   **Operador**: Reporta nuevos incidentes
-   **Incident Commander**: Coordina la respuesta, asigna recursos, escala si es necesario
-   **Technical Responder**: Investiga y resuelve el incidente
-   **Incident Manager**: Supervisa incidentes, cambia severidad
-   **Administrador**: Control total del sistema

### Casos de Uso Principales

| Caso de Uso | Actor | Descripción |
|-------------|-------|-------------|
| Crear Incidente | Operador, Administrador | Reportar un nuevo incidente |
| Triar Incidente | Commander | Evaluar y asignar severidad |
| Asignar Incidente | Commander | Asignar a un respondedor |
| Actualizar Estado | Commander | Cambiar estado del incidente |
| Agregar Comentario | Operador, Commander, Responder | Agregar nota al timeline |
| Cambiar Severidad | Manager, Administrador | Modificar nivel de severidad |
| Escalar Incidente | Commander | Escalar a nivel superior |
| Cerrar Incidente | Commander, Administrador | Cerrar formalmente |

## Diagrama de Secuencia

El diagrama de secuencia muestra el flujo de interacciones para crear y procesar un incidente.

![Diagrama de Secuencia](../resources/images/IncidentFlowSequence.svg)

### Flujo Principal

1.  Operador crea incidente (estado OPEN)
2.  Commander revisa y tria (asigna severidad, estado TRIAGED)
3.  Commander asigna a Technical Responder (estado ASSIGNED)
4.  Responder inicia trabajo (estado IN_PROGRESS)
5.  Responder implementa solución (estado RESOLVED)
6.  Commander revisa y cierra (estado CLOSED)

## Diagrama de Clases

El diagrama de clases muestra el modelo de dominio y las relaciones entre entidades.

![Diagrama de Clases](../resources/images/IncidentFlowClass.svg)

### Entidades Principales

-   **Incidente**: Representa un incidente reportadoc
    -   Atributos: id, título, descripción, severidad, estado, asignado_a, creado_por
    -   Métodos: triar(), asignar(), iniciar(), resolver(), cerrar(), escalar()

-   **Usuario**: Representa un usuario del sistema
    -   Atributos: id, nombre, email, rol
    -   Roles: Admin, Operator, Incident Commander, Technical Responder, Incident Manager

-   **Comentario**: Nota en la línea de tiempo del incidente
    -   Atributos: id, incidente_id, usuario_id, contenido, timestamp

-   **Notificación**: Alerta enviada a usuarios
    -   Atributos: id, usuario_id, tipo, mensaje, leída
    -   Tipos: assigned, escalated, resolved

-   **Log**: Registro de auditoría
    -   Atributos: id, incidente_id, usuario_id, acción, timestamp
    -   Acciones: created, triaged, assigned, state_changed, severity_changed, comment_added

### Relaciones

-   Incidente 1 → * Comentario
-   Incidente 1 → * Log
-   Incidente 1 → * Notificación
-   Usuario 1 → * Comentario
-   Usuario 1 → * Log
-   Usuario 1 → * Notificación
-   Incidente * → 1 Usuario (asignado_a)
-   Incidente * → 1 Usuario (creado_por)

## Reglas de Negocio

### Reglas de Transición de Estado

1.  Un incidente debe ser triado antes de ser asignado
2.  Un incidente debe tener asignado un respondedor antes de pasar a IN_PROGRESS
3.  Un incidente CRITICAL no puede cerrarse sin un resumen de resolución
4.  Una vez CLOSED, un incidente no puede volver a IN_PROGRESS

### Reglas de Notificación

1.  Incident Commander recibe notificaciones de todos los incidentes CRITICAL
2.  Incident Manager recibe notificaciones de todos los incidentes CRITICAL
3.  El respondedor asignado recibe notificaciones cuando se le asigna un incidente
4.  Todos los involucrados reciben notificaciones cuando el estado cambia a RESOLVED

### Reglas de Auditoría

1.  Cada cambio de estado genera un log de auditoría
2.  Cada cambio de severidad genera un log de auditoría
3.  Cada asignación genera un log de auditoría
4.  Los logs no pueden ser borrados ni editados

### Reglas de Permisos

| Acción | Admin | Operator | Commander | Responder | Manager |
|--------|-------|-----------|-----------|-----------|---------|
| Crear Incidente | ✓ | ✓ | ✗ | ✗ | ✗ |
| Ver Incidentes | ✓ | ✓ | ✓ | ✓ | ✓ |
| Triar | ✓ | ✗ | ✓ | ✗ | ✗ |
| Asignar | ✓ | ✗ | ✓ | ✗ | ✗ |
| Cambiar Estado | ✓ | ✗ | ✓ | ✗ | ✗ |
| Agregar Comentario | ✓ | ✓ | ✓ | ✓ | ✗ |
| Cambiar Severidad | ✓ | ✗ | ✗ | ✗ | ✓ |
| Ver Dashboard | ✓ | ✗ | ✗ | ✗ | ✓ |
| Ver Auditoría | ✓ | ✗ | ✗ | ✗ | ✗ |

## Notas de Implementación

### Tecnologías

-   **Backend**: FastAPI (Python 3.11+)
-   **Frontend**: Streamlit
-   **Base de Datos**: PostgreSQL
-   **ORM**: SQLAlchemy
-   **Arquitectura**: Hexagonal

### Consideraciones de Diseño

1.  La separación entre capas permite cambio de implementación sin afectar otras capas
2.  Los casos de uso encapsulan la lógica de negocio
3.  Los puertos definen interfaces que pueden ser implementadas de diferentes maneras
4.  Los eventos permiten notificaciones asíncronas y trazabilidad
