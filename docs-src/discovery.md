---
title: Discovery Document - IncidentFlow
---

## Resumen Ejecutivo

**IncidentFlow** es una plataforma centralizada para gestionar incidentes operativos críticos. Actualmente, los equipos coordinan respuestas a través de canales dispersos (chats, emails), lo que genera pérdida de contexto, responsables poco claros y poca visibilidad para managers.

La solución propuesta centraliza la gestión de incidentes con:
- Responsables claramente asignados
- Severidad y estados bien definidos
- Timeline confiable de acciones y cambios
- Notificaciones inmediatas para incidentes críticos
- Cierre formal con resumen y auditoría

## Contexto del Negocio

La empresa opera servicios críticos. Cuando surgen problemas (pagos fallando, integraciones caídas, errores masivos, alertas de seguridad), los equipos se coordinan por chats dispersos, lo que impacta:

- **Pérdida de contexto**: no hay histórico centralizado
- **Responsables poco claros**: muchas personas actuando sin coordinación
- **Poca visibilidad**: managers no saben el estado real
- **Sin auditoría formal**: difícil revisar qué pasó y aprender
- **Escalamientos ad-hoc**: no hay proceso definido

## Usuarios y Roles

| Rol | Responsabilidad | Permisos |
|-----|-----------------|----------|
| **Operator** | Reporta incidentes y agrega contexto | Crear incidentes, comentar |
| **Incident Commander** | Coordina el incidente, asigna responsables, cambia estados | Asignar, escalar, cambiar estados, comentar |
| **Technical Responder** | Trabaja en la solución, comenta avances | Comentar, registrar acciones técnicas |
| **Manager** | Consulta estado, severidad e impacto | Lectura de incidentes, dashboards |
| **Admin** | Visibilidad total, reasignaciones | Todo (lectura, escritura, auditoría, usuarios) |

## Requerimientos Funcionales

### RF-01: Creación de Incidentes
- Usuario autenticado puede crear un incidente
- Campos: título, descripción, severidad (LOW/MEDIUM/HIGH/CRITICAL)
- Estado inicial: OPEN
- Evento: INCIDENT_CREATED publicado

### RF-02: Triaje y Asignación
- Incident Commander puede cambiar estado a TRIAGED
- Incident Commander puede asignar a responsable
- Solo Incident Commander/Admin pueden cambiar severidad
- Evento: INCIDENT_ASSIGNED publicado

### RF-03: Timeline y Comentarios
- Todos pueden agregar comentarios
- Timeline centralizado: comentarios, cambios de estado, cambios de severidad, asignaciones
- Cada entrada registra: usuario, timestamp, qué cambió

### RF-04: Notificaciones de Eventos
- CRITICAL: notifica Commander y Manager inmediatamente
- Cambio de severidad: notifica Commander y Manager
- Asignación: notifica al responsable asignado
- Resolución: notifica al creador y Manager

### RF-05: Reglas de Negocio para CRITICAL
- CRITICAL no puede cerrarse sin resumen
- CRITICAL notifica inmediatamente
- Requiere responsable asignado
- Timeline debe quedar bien documentado

### RF-06: Restricciones de Transición de Estado
- No puede pasar a IN_PROGRESS sin responsable asignado
- Incidente CLOSED no vuelve a IN_PROGRESS
- Solo Commander/Admin pueden resolver o cerrar
- Cambios de severidad deben auditarse

### RF-07: Auditoría
- Cada cambio se registra en AuditLog
- Quién lo hizo, cuándo, qué cambió
- Accessible solo para Admin y con restricciones para Manager

## Requerimientos No Funcionales

- **Seguridad**: Autenticación de usuarios, autorización por rol, validación de permisos
- **Trazabilidad**: Audit trail completo de todas las operaciones
- **Disponibilidad**: Sistema debe estar disponible durante incidentes
- **Usabilidad**: Interfaz clara y rápida para responder incidentes
- **Mantenibilidad**: Código limpio, arquitectura bien separada
- **Performance**: Respuestas rápidas (<200ms para queries comunes)

## Reglas de Negocio

1. Las severidades son: LOW, MEDIUM, HIGH, CRITICAL
2. CRITICAL requiere notificación inmediata a Commander y Manager
3. CRITICAL no puede cerrarse sin resumen de resolución
4. CRITICAL debe tener responsable asignado
5. Un incidente CLOSED no vuelve a estados anteriores (IN_PROGRESS)
6. No puede pasar a IN_PROGRESS sin responsable asignado
7. Cambios de severidad deben auditarse
8. Solo Incident Commander o Admin pueden resolver/cerrar incidentes
9. Todos los cambios se registran en timeline con usuario, timestamp y detalles
10. Las notificaciones se publican en eventos del sistema

## Estados del Flujo Principal

```
OPEN → TRIAGED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
  ↘ CANCELLED
  ↘ ESCALATED
```

### Descripción de Estados

- **OPEN**: Incidente recién reportado, sin triaje
- **TRIAGED**: Se evaluó la severidad e impacto inicial
- **ASSIGNED**: Se asignó a un responsable técnico
- **IN_PROGRESS**: El responsable está trabajando en la solución
- **RESOLVED**: Se implementó la solución, falta cierre formal
- **CLOSED**: Incidente cerrado con resumen y auditoría completa
- **ESCALATED**: Se escaló a nivel superior (puede volver a IN_PROGRESS)
- **CANCELLED**: Se descartó (no era incidente real o fue falsa alarma)

### Transiciones Válidas e Inválidas

| Desde | Hacia | Válido | Restricción |
|-------|-------|--------|------------|
| OPEN | TRIAGED | ✓ | - |
| TRIAGED | ASSIGNED | ✓ | Debe haber responsable |
| ASSIGNED | IN_PROGRESS | ✓ | Debe tener responsable |
| IN_PROGRESS | RESOLVED | ✓ | - |
| RESOLVED | CLOSED | ✓ | CRITICAL debe tener resumen |
| CLOSED | cualquiera | ✗ | Bloqueado |
| cualquiera | ESCALATED | ✓ | Puede escalar en cualquier momento |
| cualquiera | CANCELLED | ✓ | Puede cancelar en cualquier momento |

## Eventos del Sistema

- **INCIDENT_CREATED**: Cuando se crea un incidente
- **INCIDENT_TRIAGED**: Cuando se marca como triageado
- **INCIDENT_ASSIGNED**: Cuando se asigna responsable
- **SEVERITY_CHANGED**: Cuando cambia la severidad
- **INCIDENT_ESCALATED**: Cuando se escalada
- **COMMENT_ADDED**: Cuando se agrega comentario
- **INCIDENT_RESOLVED**: Cuando se resuelve
- **INCIDENT_CLOSED**: Cuando se cierra formalmente

Cada evento debe indicar:
- Cuándo ocurrió (timestamp)
- Quién lo disparó (usuario)
- Qué datos contiene (detalles relevantes)
- Si genera notificación
- Si se registra en auditoría

## Notificaciones

### Eventos que Notifican

| Evento | A Quién | Prioridad | Canal (MVP) |
|--------|---------|-----------|------------|
| INCIDENT_CREATED (CRITICAL) | Commander, Manager | ALTA | En-memory |
| INCIDENT_ASSIGNED | Responsable asignado | MEDIA | En-memory |
| SEVERITY_CHANGED | Commander, Manager | ALTA | En-memory |
| INCIDENT_RESOLVED | Creator, Manager | MEDIA | En-memory |
| COMMENT_ADDED | Participantes | BAJA | En-memory |

En MVP: notificaciones se almacenan en base de datos y se muestran en UI. No hay integración real con Slack/email/PagerDuty (fuera de alcance).

## Alcance MVP

✓ Incluido:
- Creación y gestión de incidentes
- Estados y transiciones con restricciones
- Asignación de responsables
- Timeline centralizado con comentarios
- Auditoría de cambios
- Notificaciones en-memory
- Dashboard por rol (Operator, Commander, Manager, Admin)
- Autenticación y autorización básica
- API REST + Frontend Streamlit
- Docker Compose para desarrollo
- CI/CD en GitHub Actions
- Deployment en Render (dev/prod)

✗ Fuera de Alcance:
- Monitoreo automático de sistemas
- Integración real con PagerDuty
- Integración real con Slack
- Generación automática de postmortem
- Alertas desde sistemas externos
- Calendario de on-call
- Integraciones complejas de SSO

## Riesgos, Supuestos y Preguntas Abiertas

### Riesgos Técnicos
- Performance bajo alta concurrencia (muchos comentarios simultáneos)
  - Mitigación: caching de incident list, normalizar queries
- Inconsistencia de datos si notificaciones fallan
  - Mitigación: event bus con retry, auditoría completa

### Supuestos
- Los usuarios se autenticarán con credenciales simples (no OAuth complejo)
- Los incidentes son de corta duración (horas, no días)
- La empresa tiene <500 usuarios
- PostgreSQL es suficiente (no necesita sharding)

### Preguntas Abiertas
- ¿Hay integración con algún sistema de monitoreo existente?
- ¿Cuál es el SLA esperado para respuesta a CRITICAL?
- ¿Se necesita granularidad horaria o minutos en timestamps?
- ¿Hay límite de tamaño para descripciones/comentarios?
- ¿Multi-tenant o single-tenant?

## Definición de Listo (DoD)

Cada historia de usuario debe cumplir:
- Criterios de aceptación claros
- Pruebas automatizadas (>80% cobertura)
- Documentación de API (si corresponde)
- Auditoría funciona correctamente
- Sin breaking changes en APIs previas
