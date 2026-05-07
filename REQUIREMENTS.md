# Caso 4: IncidentFlow

## Plataforma de escalamiento de incidentes operativos

### Contexto que pueden contar al inicio

La empresa opera servicios críticos. Cuando hay problemas como pagos fallando, integraciones caídas, errores masivos o alertas de seguridad, los equipos se coordinan por chats dispersos.

Eso genera pérdida de contexto, responsables poco claros y poca visibilidad para managers.

Pueden decir algo como:

> "Queremos centralizar la gestión de incidentes para tener responsables, estados, severidad, timeline y cierre formal."

## Dolor principal

Durante un incidente no queda claro quién está a cargo, qué severidad tiene, qué acciones se tomaron, quién fue notificado, si el incidente está resuelto y qué aprendizaje quedó al final.

## Usuarios del negocio

* **Operator**: reporta incidentes y agrega contexto
* **Incident Commander**: coordina el incidente, asigna responsables y cambia estados
* **Technical Responder**: trabaja en la solución y comenta avances
* **Manager**: consulta estado, severidad e impacto
* **Admin**: tiene visibilidad total y puede reasignar

## Cartas ocultas del cliente

### Carta oculta 1: Severidades

**Revelar solo si preguntan por severidad, prioridad, impacto o criticidad.**

Las severidades son:

* LOW
* MEDIUM
* HIGH
* CRITICAL

Pueden decir:

> "La severidad es clave porque no todos los incidentes requieren la misma respuesta."

### Carta oculta 2: Reglas para incidentes críticos

**Revelar solo si preguntan por reglas especiales para incidentes críticos.**

Los incidentes **CRITICAL** tienen reglas especiales:

* notifican inmediatamente al Incident Commander y Manager;
* no pueden cerrarse sin resumen;
* deben tener responsable asignado;
* su timeline debe quedar bien registrado.

Pueden decir:

> "Cuando algo es crítico, necesitamos visibilidad inmediata y cierre formal."

### Carta oculta 3: Permisos por rol

**Revelar solo si preguntan quién puede hacer qué.**

Reglas de permisos:

* Operator puede crear incidentes y comentar
* Incident Commander puede asignar, escalar y cambiar estados
* Technical Responder puede comentar y marcar acciones técnicas como realizadas
* Manager consulta estado e impacto
* Admin puede ver y reasignar todo

Pueden decir:

> "No queremos que cualquier persona cierre o resuelva incidentes críticos."

### Carta oculta 4: Restricciones de estado

**Revelar solo si preguntan por transiciones inválidas o restricciones del flujo.**

Reglas importantes:

* Un incidente cerrado no vuelve a **IN_PROGRESS**
* Todo cambio de severidad debe auditarse
* No puede pasar a **IN_PROGRESS** sin responsable
* Solo Incident Commander o Admin puede pasar a **RESOLVED** o **CLOSED**

Pueden decir:

> "El flujo debe protegernos de cierres informales o cambios sin responsable."

### Carta oculta 5: Chat, comentarios y timeline

**Revelar solo si preguntan por colaboración, comentarios, timeline o historial.**

Para nosotros el timeline es central. Durante un incidente, los comentarios y actualizaciones son más importantes que reportes avanzados.

Necesitamos registrar:

* comentarios;
* cambios de estado;
* cambios de severidad;
* responsables asignados;
* acciones relevantes;
* resumen de cierre.

Pueden decir:

> "El sistema debe servir durante el incidente y también después, para revisar qué pasó."

### Carta oculta 6: Estados del flujo

**Revelar solo si preguntan por ciclo de vida o estados.**

Flujo sugerido:

```
OPEN → TRIAGED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
  ↘ CANCELLED
  ↘ ESCALATED
```

### Carta oculta 7: Eventos y notificaciones

**Revelar solo si preguntan por notificaciones, eventos o auditoría.**

Eventos importantes:

* INCIDENT_CREATED
* INCIDENT_TRIAGED
* INCIDENT_ASSIGNED
* SEVERITY_CHANGED
* INCIDENT_ESCALATED
* COMMENT_ADDED
* INCIDENT_RESOLVED
* INCIDENT_CLOSED

Notificaciones esperadas:

* Incidente creado: notifica al Incident Commander.
* Incidente crítico: notifica Incident Commander y Manager.
* Incidente asignado: notifica al responsable.
* Cambio de severidad: notifica al Commander y Manager.
* Incidente resuelto: notifica al creador y Manager.
* Comentario agregado: puede notificar a participantes del incidente.

### Carta oculta 8: Fuera de alcance

**Revelar solo si preguntan qué NO entra en el MVP.**

No entra en MVP:

* monitoreo automático;
* integración real con PagerDuty;
* integración real con Slack;
* generación automática de postmortem;
* alertas desde sistemas externos;
* calendario de on-call.

Pueden decir:

> "Por ahora la prioridad es centralizar el flujo manual y dejar trazabilidad confiable."

## Requerimientos ocultos a evaluar

**Requerimiento oculto | ¿Lo descubrieron?**

* Existen severidades LOW, MEDIUM, HIGH y CRITICAL
* CRITICAL notifica inmediatamente
* CRITICAL no se cierra sin resumen
* No pasa a IN_PROGRESS sin responsable
* Cerrado no vuelve a IN_PROGRESS
* Cambio de severidad debe auditarse
* Solo Commander/Admin resuelve o cierra
* Chat/comentarios por incidente es prioritario
* No hay integración real con PagerDuty/Slack en MVP
* Debe existir timeline confiable
