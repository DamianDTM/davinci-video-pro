---
name: davinci-video-pro
description: Instala y conecta DaVinci Resolve con su MCP, Gemini y Omni en Codex o Claude Code; edita videos a partir del guion del usuario con subtitulos, recursos y exportacion. Usala al configurar este flujo, editar otro video o retomar un montaje.
metadata:
  version: "2.0.0"
  short-description: Guion primero, instalacion guiada y edicion profesional
---

# DaVinci Video Pro

Skill portable para Codex y Claude Code con acceso local al equipo. Habla en el
idioma del usuario. Lee [clientes](references/clientes.md) al instalar o cambiar
de asistente. Cada persona aporta sus cuentas, claves, capacidades y materiales.

## Regla obligatoria: pedir el guion antes de APIs o edicion

ANTES de editar un video o llamar a cualquier API de este flujo, pide al usuario
su guion y usalo como FUENTE PRINCIPAL de la edicion. Esto incluye consultas MCP
de Resolve, pruebas de credenciales, catalogos de modelos, analisis Gemini,
generacion Omni e imagenes. Una llamada de prueba tambien requiere guion.

Primera pregunta: «Pasame el guion que quieres seguir. Si no tienes uno, dime el
objetivo, el mensaje y como quieres que se vea el video para preparar un borrador».
Si ya lo entrego en este encargo, leelo y registralo; no lo pidas otra vez. Una
plantilla o preferencias de otro video NO son el guion del nuevo video.

Si no hay guion, preparar un borrador desde las indicaciones del usuario sin
llamar servicios audiovisuales, presentarlo y esperar confirmacion. Si solo desea
instalar, pueden copiarse la skill y revisarse archivos locales; las comprobaciones
mediante API y los instaladores que hacen pruebas quedan pendientes del guion.

Guardar el guion en GUION-CREATIVO.md, conservar su texto fuente y registrar la
entrega/confirmacion con workflow.py confirm-script. Ejecutar workflow.py gate
antes de APIs, instaladores con pruebas de conexion y operaciones de edicion.
Los helpers de Google tambien lo verifican antes de crear clientes. Esto no
autoriza subir toda una carpeta ni gastar sin limite.

## Documentos y continuidad

1. Inicializar una carpeta por video con scripts/workflow.py --project-dir <carpeta>
   init. Leer [continuidad](references/continuidad.md). GUION-CREATIVO.md define
   mensaje, estructura y apariencia. BRIEF-TECNICO.md define correcciones y calidad.
   Los valores predeterminados se adaptan al guion del usuario.
2. Al retomar leer ESTADO.md, los dos documentos, TAREAS.md y CAMBIOS-PENDIENTES.md.
   Mantener pendientes, rutas y revisiones en disco. No crear otro task/chat salvo
   peticion expresa; una lista de tareas es una lista de comprobacion.
3. Recoger las mejoras durante el trabajo. Al cerrar una ronda, resumir por
   documento los cambios y su alcance: este video o preferencias para futuros
   videos. PREGUNTAR si el resumen es correcto y esperar la respuesta.
4. Tras confirmar, actualizar ambos documentos de forma coordinada, cada uno con
   sus cambios pertinentes, sustituyendo instrucciones obsoletas. Usar las
   revisiones preparadas de workflow.py para conservar historial y estado.
5. Actualizar plantillas compartidas solo con preferencias generales confirmadas.
   Guardarlas fuera del paquete en ~/.davinci-video-pro/templates o en
   DAVINCI_VIDEO_PRO_HOME. Cada video nuevo requiere contenido y guion propios.
   Nunca heredar claves, autorizaciones o presupuestos de otra persona/proyecto.

## Configuracion y produccion

Con guion vigente, seguir [instalacion](references/instalacion.md). Ruta probada:
Windows, Resolve Free 21.0.3.7 y MCP de Samuel Gursky 2.224.1. Verificar compatibilidad
actual, reutilizar instalaciones funcionales y preservar proyectos al cambiar
versiones. Guardar el avance antes de un reinicio. Al recibir «listo», comprobar.

- [Gemini](references/gemini.md): gemini-3.8-flash preferido. Comprender imagen y voz,
  relacionar el material con el guion y verificar tiempos antes de cortar.
- [Omni](references/omni.md): gemini-omni-1.1-flash preferido. Planificar perspectivas
  por escena y presupuesto; revisar cada resultado antes de integrarlo.
- [Recursos](references/recursos.md): imagenes distintas, pertinentes y coherentes.
  Descubrir herramientas en cada cliente; Claude no hereda ImageGen de Codex.
- [Edicion](references/edicion.md): recepcion, montaje, subtitulos, QA y entrega.
- [Resolve practico](references/resolve-practico.md): API, Fusion y render; leer
  al trabajar con esas operaciones.

Conservar voz y significado; corregir silencios accidentales, repeticiones y
tropiezos corregibles. Subtitulos con enfasis selectivo, CTA cuando la voz lo pida,
recursos unicos y transiciones adecuadas al ritmo. No forzar recursos contra el
guion ni prometer recuperar una toma real inexistente o sincronizacion generativa exacta.

## Evidencia y entrega

Mostrar TAREAS.md con pendiente/en curso/hecho/no aplicable justificado. Marcar
hecho solo con evidencia: archivo, revision visual/auditiva, consulta o render
verificado. Conexion, montaje y exportacion se comprueban por separado.

Entregar enlace y ruta absoluta del MP4 completo mas reciente, proyecto editable
con recursos, SRT y ambos documentos vigentes. Conservar revisiones. Si quedan
cambios documentales pendientes, mostrar el resumen y preguntar; no declararlos
confirmados. Guardar el siguiente paso para otro chat.

Pedir intervencion cuando sea necesaria indicando app, accion y resultado esperado.
Reutilizar autorizaciones dadas. Tras dos fallos iguales sin evidencia nueva,
registrar la causa y pedir la accion que falta. Ante un gasto incierto de Omni,
inspeccionar el intento antes de otro. No publicar ni enviar a terceros por defecto.
