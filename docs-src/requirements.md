---
title: Requirements - IncidentFlow System
---

## Requerimientos Funcionales

### RF-01: Autenticación y Gestión de Usuarios

**Como** usuario del sistema,
**Quiero** autenticarme con credenciales,
**Para** acceder a la plataforma según mi rol.

**Descripción:**
- Sistema de autenticación básica (email + password)
- Validación de usuario y asignación de rol automático
- Roles disponibles: Operator, Commander, Responder, Manager, Admin
- Sessions/tokens para mantener autenticación
- Logout funcional

**Criterios de Aceptación:**
- [ ] Usuario se autentica exitosamente
- [ ] Credenciales inválidas muestran error
- [ ] Rol se asigna correctamente después de login
- [ ] Token/session persiste durante la sesión
- [ ] Logout elimina autenticación

---

### RF-02: Crear Incidente

**Como** Operator,
**Quiero** crear un nuevo incidente,
**Para** reportar un problema operativo.

**Descripción:**
- Formulario con campos: título, descripción, severidad
- Severidades disponibles: LOW, MEDIUM, HIGH, CRITICAL
- Estado inicial: OPEN
- Creador se registra automáticamente
- Evento INCIDENT_CREATED publicado

**Criterios de Aceptación:**
- [ ] Incidente se crea con todos los campos requeridos
- [ ] Campos validados (no vacíos, longitud razonable)
- [ ] Estado inicial es OPEN
- [ ] Creador se registra correctamente
- [ ] Respuesta contiene ID del incidente creado
- [ ] Evento INCIDENT_CREATED se publica

---

### RF-03: Listar Incidentes con Filtros

**Como** usuario,
**Quiero** ver una lista de incidentes con filtros,
**Para** encontrar rápidamente incidentes relevantes.

**Descripción:**
- Lista paginada o lazy-loaded de incidentes
- Filtros por: severidad, estado, responsable asignado
- Búsqueda por título/descripción
- Visualización de resumen: id, título, severidad, estado, creador, timestamps
- Acceso según rol (todos pueden listar, pero permisos varían)

**Criterios de Aceptación:**
- [ ] Lista muestra incidentes con paginación
- [ ] Filtros funcionan independientemente
- [ ] Búsqueda por texto funciona
- [ ] Respuestas son rápidas (<200ms)
- [ ] Datos mostrados son correctos
- [ ] Usuarios sin permisos no ven incidentes sensibles

---

### RF-04: Ver Detalle de Incidente

**Como** usuario,
**Quiero** ver el detalle completo de un incidente,
**Para** entender el contexto y estado actual.

**Descripción:**
- Página con toda la información del incidente
- Timeline centralizado: comentarios, cambios de estado, cambios de severidad, asignaciones
- Cada entrada en timeline muestra: usuario, timestamp, acción, detalles
- Información mostrada: id, título, descripción, severidad, estado, creador, responsable, timestamps

**Criterios de Aceptación:**
- [ ] Página carga correctamente
- [ ] Timeline muestra todas las acciones en orden cronológico
- [ ] Información está actualizada
- [ ] Usuarios sin permisos no pueden ver datos sensibles

---

### RF-05: Cambiar Estado del Incidente

**Como** Incident Commander,
**Quiero** cambiar el estado del incidente,
**Para** coordinar la respuesta.

**Descripción:**
- Transiciones válidas según máquina de estados
- Solo Commander/Admin pueden cambiar estado
- Validaciones:
  - No puede pasar a IN_PROGRESS sin responsable asignado
  - No puede cerrarse sin resumen (CRITICAL)
  - Incidente CLOSED no vuelve a IN_PROGRESS
- Evento INCIDENT_STATE_CHANGED publicado
- AuditLog registra el cambio

**Criterios de Aceptación:**
- [ ] Transiciones válidas funcionan
- [ ] Transiciones inválidas son rechazadas con error claro
- [ ] Solo usuarios autorizados pueden cambiar estado
- [ ] Evento se publica correctamente
- [ ] AuditLog registra usuario, timestamp, cambio

---

### RF-06: Asignar Responsable

**Como** Incident Commander,
**Quiero** asignar un técnico responsable,
**Para** que sepa quién debe resolver el incidente.

**Descripción:**
- Dropdown con lista de Technical Responders disponibles
- Solo Commander/Admin pueden asignar
- Validación: responsable debe estar activo
- Evento INCIDENT_ASSIGNED publicado
- Notificación enviada al responsable asignado

**Criterios de Aceptación:**
- [ ] Dropdown muestra usuarios válidos
- [ ] Asignación se registra correctamente
- [ ] Responsable recibe notificación
- [ ] AuditLog registra la asignación
- [ ] Evento se publica

---

### RF-07: Cambiar Severidad

**Como** Incident Commander,
**Quiero** ajustar la severidad de un incidente,
**Para** reflejar el impacto actual.

**Descripción:**
- Cambio de severidad: LOW ↔ MEDIUM ↔ HIGH ↔ CRITICAL
- Solo Commander/Admin pueden cambiar
- Si CRITICAL: notifica inmediatamente a Commander y Manager
- Evento SEVERITY_CHANGED publicado
- AuditLog registra cambio + quién lo hizo

**Criterios de Aceptación:**
- [ ] Cambio de severidad funciona
- [ ] Solo autorizados pueden hacerlo
- [ ] Si CRITICAL: se envían notificaciones inmediatas
- [ ] AuditLog registra valores antiguos y nuevos
- [ ] Evento se publica

---

### RF-08: Agregar Comentarios

**Como** usuario autorizado,
**Quiero** agregar comentarios a un incidente,
**Para** colaborar y dejar registro de acciones.

**Descripción:**
- Todos los usuarios autenticados pueden comentar
- Campo de texto libre para comentario
- Se registra automáticamente: autor, timestamp, texto
- Comentarios aparecen en timeline inmediatamente
- Evento COMMENT_ADDED publicado

**Criterios de Aceptación:**
- [ ] Comentario se crea y aparece en timeline
- [ ] Se registra autor y timestamp correctamente
- [ ] Comentarios no pueden estar vacíos
- [ ] Evento se publica
- [ ] AuditLog registra el comentario

---

### RF-09: Reglas CRITICAL

**Como** sistema,
**Quiero** enforcer reglas especiales para CRITICAL,
**Para** asegurar respuesta inmediata y resolución formal.

**Descripción:**
- CRITICAL notifica inmediatamente a Commander y Manager al crearse
- CRITICAL no puede cerrarse sin resumen de resolución
- CRITICAL debe tener responsable asignado antes de IN_PROGRESS
- Cambios de severidad en CRITICAL se auditan estrictamente

**Criterios de Aceptación:**
- [ ] CRITICAL genera notificaciones inmediatas
- [ ] Intento de cerrar sin resumen es rechazado
- [ ] No puede entrar a IN_PROGRESS sin asignado
- [ ] AuditLog muestra todos los cambios
- [ ] Sistema valida reglas correctamente

---

### RF-10: Timeline y Auditoría

**Como** Manager/Admin,
**Quiero** ver el timeline completo y audit log,
**Para** revisar qué pasó y cumplir regulaciones.

**Descripción:**
- Timeline visual: comentarios, cambios, asignaciones
- Audit Log con: quién, qué, cuándo, valores antiguos/nuevos
- Cada acción registrada con metadata completa
- Búsqueda en audit log por usuario/fecha/acción

**Criterios de Aceptación:**
- [ ] Timeline muestra todas las acciones
- [ ] Audit Log es completo y exacto
- [ ] Datos de auditoría no pueden ser modificados
- [ ] Búsqueda en audit log funciona
- [ ] Managers ven solo auditoría, Admins ven todo

---

### RF-11: Notificaciones por Eventos

**Como** usuario,
**Quiero** recibir notificaciones de eventos relevantes,
**Para** estar siempre informado.

**Descripción:**
- Eventos que notifican:
  - INCIDENT_CREATED (CRITICAL): notifica Commander, Manager
  - INCIDENT_ASSIGNED: notifica responsable asignado
  - SEVERITY_CHANGED: notifica Commander, Manager
  - INCIDENT_RESOLVED: notifica creador, Manager
  - COMMENT_ADDED (optional): notifica participantes
- Notificaciones almacenadas en DB
- Interfaz para ver notificaciones no leídas
- Marcar como leída

**Criterios de Aceptación:**
- [ ] Notificaciones se crean automáticamente
- [ ] Se almacenan en base de datos
- [ ] Usuario ve notificaciones en dashboard
- [ ] Puede marcar como leída
- [ ] Sin integración Slack/email en MVP

---

### RF-12: Dashboards por Rol

**Como** usuario con rol específico,
**Quiero** ver un dashboard adaptado a mi rol,
**Para** ver información relevante de un vistazo.

**Descripción:**
- **Operator**: lista de incidentes, crear nuevo
- **Commander**: incidentes asignados, pendientes, timeline detallado
- **Manager**: métricas, distribución por severidad, incidentes CRITICAL sin resolver
- **Admin**: todos los datos, gestión de usuarios, audit log

**Criterios de Aceptación:**
- [ ] Cada rol ve su dashboard customizado
- [ ] Datos son correctos y actualizados
- [ ] No hay información que el rol no debería ver
- [ ] Dashboard carga rápido

---

## Requerimientos No Funcionales

### RNF-01: Seguridad

- Autenticación obligatoria para todas las funciones
- Autorización por rol en cada endpoint
- Validación de entrada en todos los formularios
- Protección contra inyecciones SQL (uso de ORM)
- HTTPS en producción
- Tokens seguros (JWT o similar)

### RNF-02: Performance

- Respuestas API <200ms para operaciones comunes
- Lista de incidentes carga en <1s incluso con miles de registros
- Queries optimizadas (indexes en campos de filtrado)
- Caching de datos comunes

### RNF-03: Escalabilidad

- Arquitectura preparada para crecer (clean architecture)
- Repositorios abstractos (fácil cambiar DB)
- Event bus preparado para múltiples handlers
- Sin acoplamiento entre capas

### RNF-04: Disponibilidad

- Sistema debe estar disponible 24/7 durante incidentes
- Graceful degradation si algún servicio falla
- Backups de base de datos
- Rollback rápido en caso de error

### RNF-05: Mantenibilidad

- Código limpio y documentado
- Commits pequeños y descriptivos
- Tests con >80% cobertura
- Documentación clara de API y arquitectura

### RNF-06: Trazabilidad

- Audit log completo de todas las operaciones
- Datos de auditoría inmutables
- Timeline precisamente ordenado (con microsegundos si es necesario)
- Logs de aplicación centralizados

### RNF-07: Usabilidad

- Interfaz intuitiva para roles sin conocimiento técnico
- Mensajes de error claros y en español
- Validación en tiempo real
- Dark mode opcional

### RNF-08: Compatibilidad

- Compatible con navegadores modernos (Chrome, Firefox, Safari, Edge)
- Streamlit versión stable (compatible con Python 3.11+)
- FastAPI v0.100+
- PostgreSQL 13+

---

## Reglas de Negocio

### RN-01: Máquina de Estados

Estados válidos:
- **OPEN**: Inicial, recién reportado
- **TRIAGED**: Evaluado por Commander
- **ASSIGNED**: Asignado a responsable
- **IN_PROGRESS**: Responsable trabajando
- **RESOLVED**: Solución implementada
- **CLOSED**: Formal closure completado
- **ESCALATED**: Escalado (puede volver a ASSIGNED o IN_PROGRESS)
- **CANCELLED**: False alarm o cancelado

Transiciones bloqueadas:
- CLOSED → cualquier otro estado (terminal)
- Cualquier → IN_PROGRESS sin responsable asignado
- RESOLVED → CLOSED sin resumen (CRITICAL)

### RN-02: Severidades

- **LOW**: Molestias menores, puede esperar
- **MEDIUM**: Afecta algunos usuarios, debe resolverse hoy
- **HIGH**: Afecta muchos usuarios, requiere atención inmediata
- **CRITICAL**: Servicio crítico caído, requiere respuesta inmediata del Commander

### RN-03: Reglas CRITICAL

- Notificación inmediata al crear
- No puede cerrarse sin resumen
- Requiere responsable asignado
- Cambios de severidad auditados estrictamente
- Solo Commander/Admin pueden cerrar

### RN-04: Permisos por Rol

| Acción | Operator | Commander | Responder | Manager | Admin |
|--------|----------|-----------|-----------|---------|-------|
| Crear Incidente | ✓ | ✓ | ✗ | ✗ | ✓ |
| Cambiar Estado | ✗ | ✓ | Parcial | ✗ | ✓ |
| Asignar | ✗ | ✓ | ✗ | ✗ | ✓ |
| Cambiar Severidad | ✗ | ✓ | ✗ | ✗ | ✓ |
| Comentar | ✓ | ✓ | ✓ | ✗ | ✓ |
| Ver Incidentes | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ver Audit Log | ✗ | ✗ | ✗ | ✓ | ✓ |
| Gestionar Usuarios | ✗ | ✗ | ✗ | ✗ | ✓ |

### RN-05: Auditoría

Cada operación registra:
- Usuario que la realizó
- Timestamp exacto
- Acción realizada
- Valores antiguos y nuevos (para cambios)
- Metadata adicional relevante

Datos no pueden ser modificados o eliminados después de creados.

### RN-06: Timeline

- Todos los comentarios, cambios de estado, asignaciones en timeline centralizado
- Orden estrictamente cronológico
- Cada entrada muestra qué cambió y quién lo hizo
- Información es la fuente de verdad para revisar qué pasó

### RN-07: Notificaciones

Eventos que generan notificación:
- INCIDENT_CREATED (CRITICAL): Commander, Manager (inmediato)
- INCIDENT_ASSIGNED: responsable asignado
- SEVERITY_CHANGED (cualquier escala): Commander, Manager
- INCIDENT_RESOLVED: creador, Manager
- COMMENT_ADDED: participantes activos (opcional)

En MVP: almacenadas en DB, sin Slack/Email/SMS.

---

## Matriz de Trazabilidad

| Requisito | Issue | Estado |
|-----------|-------|--------|
| RF-01: Autenticación | Backend #8 | En Backlog |
| RF-02: Crear Incidente | Backend #10-11, Frontend #13-14 | En Backlog |
| RF-03: Listar + Filtros | Frontend #13 | En Backlog |
| RF-04: Ver Detalle | Frontend #14 | En Backlog |
| RF-05: Cambiar Estado | Backend #10-11, Frontend #15 | En Backlog |
| RF-06: Asignar | Backend #11, Frontend #15 | En Backlog |
| RF-07: Cambiar Severidad | Backend #11, Frontend #15 | En Backlog |
| RF-08: Comentarios | Backend #10-11, Frontend #14 | En Backlog |
| RF-09: Reglas CRITICAL | Backend #10, #12 | En Backlog |
| RF-10: Timeline + Auditoría | Backend #8-9, #10 | En Backlog |
| RF-11: Notificaciones | Backend #12 | En Backlog |
| RF-12: Dashboards | Frontend #16 | En Backlog |
| RNF-01-08 | Todos | En Backlog |

---

## Glosario

- **Incidente**: Evento operativo crítico que requiere respuesta
- **Severidad**: Nivel de impacto (LOW, MEDIUM, HIGH, CRITICAL)
- **Estado**: Posición actual en el ciclo de vida del incidente
- **Commander**: Usuario con permisos para escalar y cambiar estados
- **Timeline**: Histórico centralizado de todas las acciones
- **Audit Log**: Registro inmutable de quién hizo qué y cuándo
- **Notificación**: Alerta enviada a usuarios sobre eventos relevantes
- **Role**: Rol del usuario (Operator, Commander, Responder, Manager, Admin)

---

## Notas

- En MVP no hay integración real con PagerDuty, Slack, email
- Notificaciones en MVP son en-memory (solo visibles en la app)
- Autenticación es básica (no OAuth, SAML, etc)
- Database es PostgreSQL únicamente
- Frontend es Streamlit (no React, Vue, Angular)
