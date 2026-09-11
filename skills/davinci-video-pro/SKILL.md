---
name: davinci-video-pro
description: Instala y conecta DaVinci Resolve, su MCP y Gemini en Codex o Claude Code; organiza materiales y videos finales y edita con guion creativo y brief tecnico obligatorio, Omni e imagenes opcionales.
metadata:
  version: "2.3.0"
  short-description: Instalacion guiada y edicion con brief obligatorio
---

# DaVinci Video Pro

Skill para Codex local y Claude Code con acceso al equipo de Resolve. Hablar en
el idioma del usuario. Seguir [flujo guiado](references/flujo-guiado.md) al iniciar,
instalar o recibir otro encargo. Reutilizar las respuestas, instalaciones y permisos
vigentes; preguntar solo lo que falta. No detenerse al terminar la instalacion:
continuar directamente con la recepcion del encargo.

## Orden de trabajo obligatorio

1. **Instalacion y conexion.** Preguntar si tiene Resolve y que version/edicion;
   si no sabe, comprobar localmente. Reutilizar lo compatible. Si falta o requiere
   cambio, preparar la version compatible y preguntar por su instalacion concreta.
   Registrar el MCP en el cliente real, configurar la clave propia de Google
   localmente y dar los pasos para abrir Resolve, un proyecto y activar el puente.
   Verificar conexion. Leer [instalacion](references/instalacion.md) y
   [clientes](references/clientes.md). No pedir guion para esta etapa tecnica.
2. **Materiales y resultados.** Revisar la carpeta actual; si contiene videos,
   mostrar inventario y preguntar todos o cuales. Si no, pedir la ruta. Preguntar
   cuantos videos finales quiere y como distribuirlos. Recibir audios opcionales.
3. **Brief tecnico.** Preguntar si aporta uno o usa el predeterminado. Mostrar
   SIEMPRE su ruta absoluta editable y leerlo completo antes de producir.
4. **Guion creativo.** Preguntar propio o predeterminado y mostrar SIEMPRE la ruta
   absoluta de la copia predeterminada para leerla/editarla. Si no tiene uno, usar
   nuestro guion profesional; «hazlo con el de defecto» permite seguir sin otra
   confirmacion. Si ya lo eligio, mostrar la ruta y continuar sin volver a preguntar.
5. **Recursos.** Preguntar si quiere escenas Omni; preguntar si quiere imagenes y
   mostrar opciones de estilo y proveedores realmente disponibles. Concretar los
   archivos a enviar. Para Omni, no pedir presupuesto: usar el ciclo siguiente.
6. **Produccion y entrega.** Guardar las elecciones en ENCARGO.md, mostrar TAREAS.md
   por cada video final, analizar, editar, revisar y exportar TODOS los solicitados.

No hacer todas las preguntas de instalacion y produccion de golpe. Agrupar
preguntas relacionadas, avanzar por etapas y guardar el siguiente paso para reinicios.
Si ya esta configurado, retomar desde materiales; una comprobacion tecnica breve
no obliga a repetir la instalacion.

## Omni: generar, mostrar y esperar

NO pedir presupuesto, tope de gasto ni numero de intentos para habilitar Omni.
La eleccion real «si, usar Omni» permite preparar y generar UNA escena del guion;
reutilizarla sin otra pregunta de permiso si el envio a Google ya esta acordado.
Despues mostrar el video reproducible, su coste disponible y el registro
GASTOS-OMNI.md. Esperar la decision del usuario sobre conservarlo, ajustar/reintentar,
generar otra escena o parar. Aceptar la toma no autoriza otra generacion.
No generar lotes, alternativas ni reintentos mientras espera su revision.

Leer [Omni](references/omni.md): registrar la respuesta real con omni-next,
que habilita un solo intento. Distinguir cargo confirmado, estimacion y coste
desconocido; nunca presentar una estimacion parcial como total pagado.
Esta regla reemplaza el requisito generico de presupuesto de versiones/plantillas
anteriores. Conservar un limite que el usuario haya impuesto expresamente.

## Dos requisitos para producir

El GUION-CREATIVO.md es la fuente principal del mensaje y apariencia.
El BRIEF-TECNICO.md es OBLIGATORIO para ejecutar y revisar la edicion: LEERLO
completo y traducir sus requisitos a tareas verificables. Nunca tratarlo como
opcional ni reemplazarlo por decisiones improvisadas. Esto abarca ruidos, niveles
de voz, silencios accidentales, tartamudeos corregibles, repeticiones, palabras
completas, transiciones, subtitulos, enfasis, CTA, recursos unicos y exportacion.
Respetar excepciones expresas del usuario; no prometer corregir material irrecuperable.

Antes de analizar materiales, generar imagenes/Omni, cortar, montar o exportar,
registrar las elecciones del guion y del brief y ejecutar workflow.py gate.
Los helpers de produccion comprueban ambos documentos y sus hashes. Si falta,
cambio o esta pendiente una revision, leer su version vigente y resolverla antes
de producir. Las pruebas tecnicas de Resolve y Gemini (autenticacion, catalogo y
respuesta minima de prueba) pueden hacerse sin guion ni brief. Esta excepcion NO
permite subir videos, analizarlos, generar recursos ni editar durante instalacion.

Usar scripts/workflow.py --project-dir <carpeta> init y documents para crear y
mostrar las copias locales. Enlazar rutas absolutas reales; no mostrar <carpeta>
como si fuera una ruta util. Nunca pedir al usuario editar archivos del paquete.
Leer [continuidad](references/continuidad.md) para comandos y revisiones.

«Usa el guion por defecto», «hazlo con el de defecto» o «no tengo guion» selecciona
[nuestro guion profesional](assets/GUION-POR-DEFECTO.md): usar use-default-script
con la respuesta real, sin pedir otro guion ni repetir confirmacion. Mostrar la
ruta de GUION-CREATIVO.md una vez activado; si edito la copia de lectura antes de
elegirla, incorporar esa copia. Un borrador nuevo a medida se confirma antes de uso.

Para el brief, registrar confirm-brief con la eleccion real. Si dice «ambos por
defecto», registrar ambas elecciones de esa misma respuesta. Si no tiene brief
propio, ofrecer y aplicar el predeterminado elegido. No sobrescribir documentos
propios ni preferencias de otros proyectos al seleccionar defaults.

## Continuidad y mejoras

Al retomar leer ESTADO.md, ENCARGO.md si existe, guion, brief, TAREAS.md y
CAMBIOS-PENDIENTES.md. Conservar decisiones y rutas; no crear otro task/chat salvo
peticion expresa. Las salidas de un encargo pueden compartir materiales, pero
necesitan objetivos, montajes y exports identificables.

Recoger las mejoras durante el trabajo. Al cerrar una ronda, resumir por documento
los cambios y su alcance: video actual o preferencias para futuros videos.
Preguntar si el resumen es correcto y esperar respuesta. Tras confirmar, actualizar
ambos documentos coordinadamente con workflow.py; cada uno recibe sus cambios
pertinentes. Conservar historial y actualizar plantillas compartidas solo con
preferencias generales confirmadas en ~/.davinci-video-pro/templates o
DAVINCI_VIDEO_PRO_HOME. No heredar el discurso, autorizaciones o presupuestos de
otro video. Una eleccion previa de defaults para este encargo se reutiliza.

## Referencias de produccion

- [Gemini](references/gemini.md): modelo preferido gemini-3.8-flash; verificar imagen,
  voz, tiempos y relacion con guion y brief.
- [Omni](references/omni.md): gemini-omni-1.1-flash preferido; solo si se eligio,
  una generacion por vez, mostrando video y coste antes de decidir la siguiente.
- [Recursos](references/recursos.md): imagenes unicas y pertinentes; descubrir
  capacidades en cada host. Claude no hereda ImageGen de Codex.
- [Edicion](references/edicion.md): montaje, limpieza, subtitulos, QA y exports.
- [Resolve practico](references/resolve-practico.md): API, Fusion y render.

Ruta de referencia: Windows, Resolve Free 21.0.3.7 y MCP Samuel Gursky 2.224.1.
Verificar compatibilidad actual y conservar instalaciones funcionales.

## Evidencia y entrega

Marcar tareas hechas solo con evidencia y separar configuracion, transporte MCP,
respuesta de Resolve, montaje y exportacion. Aplicar el brief durante el montaje
Y la revision final; documentar defectos pendientes, no declararlos corregidos.

Entregar enlaces y rutas absolutas de TODOS los MP4 completos pedidos, proyectos
editables con recursos, SRT y documentos vigentes. Dar un estado por salida y
guardar el siguiente paso para otro chat. Si falta una salida o falla un requisito
tecnico, no marcar el encargo completo. Ante dos fallos iguales sin evidencia
nueva, registrar la causa y la accion necesaria. No publicar medios ni enviarlos
a terceros por defecto.
