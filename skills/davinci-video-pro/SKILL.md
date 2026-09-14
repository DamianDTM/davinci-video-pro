---
name: davinci-video-pro
description: Instala y conecta DaVinci Resolve, su MCP y Gemini en Codex o Claude Code; edita con guion y brief tecnico, documentos visuales, musica y Omni opcionales, revision previa y publicacion autorizada en redes.
metadata:
  version: "2.4.3"
  short-description: Instalacion guiada y edicion con brief obligatorio
---

# DaVinci Video Pro

Skill para Codex local y Claude Code con acceso al equipo de Resolve. Hablar en
el idioma del usuario. Seguir [flujo guiado](references/flujo-guiado.md) al iniciar,
instalar o recibir otro encargo. Reutilizar las respuestas, instalaciones y permisos
vigentes; preguntar solo lo que falta. No detenerse al terminar la instalacion:
continuar directamente con la recepcion del encargo.

## Orden de trabajo obligatorio

1. **Instalacion y conexion.** Al invocar, preguntar si ya tiene Resolve instalado
   y el puente configurado, o necesita instalarlos; reutilizar una respuesta ya dada.
   Comprobar version/edicion y conexion sin reinstalar. Si ya funciona, pasar a
   materiales o retomar la edicion pendiente. Un puente instalado pero apagado
   requiere activacion, no otra copia. Si falta o requiere
   cambio, preparar la version compatible y preguntar por su instalacion concreta.
   Completar solo lo pendiente: registrar el MCP en el cliente real, configurar la clave de Google
   localmente y dar los pasos para abrir Resolve, un proyecto y activar el puente.
   Verificar conexion. Leer [instalacion](references/instalacion.md) y
   [clientes](references/clientes.md). No pedir guion para esta etapa tecnica.
   Si no puede inspeccionar el equipo, seguir el modo guiado de instalacion.md:
   pedir solo los datos que falten, recomendar version/edicion para ese sistema,
   dar enlace oficial concreto y pasos manuales. No detenerse en «no tengo acceso».
2. **Materiales y resultados.** Revisar la carpeta actual; si contiene videos,
   mostrar inventario y preguntar todos o cuales. Si no, pedir la ruta. Preguntar
   cuantos videos finales quiere, su duracion objetivo y como distribuirlos.
   La duracion la elige el usuario; no reducir a reels breves por iniciativa propia.
3. **Brief tecnico.** Preguntar si aporta uno o usa el predeterminado. Mostrar
   SIEMPRE su ruta absoluta editable y leerlo completo antes de producir.
4. **Guion creativo.** Preguntar propio o predeterminado y mostrar SIEMPRE la ruta
   absoluta de la copia predeterminada para leerla/editarla. Si no tiene uno, usar
   nuestro guion profesional; «hazlo con el de defecto» permite seguir sin otra
   confirmacion. Si ya lo eligio, mostrar la ruta y continuar sin volver a preguntar.
5. **Recursos.** Preguntar si quiere escenas Omni; junto con las imagenes preguntar
   si aporta HTML/CSS, PDF, documentos o presentaciones, como archivos o carpeta.
   Mostrar opciones de estilo y proveedores realmente disponibles. Concretar los
   archivos a enviar. HTML y documentos son OPCIONALES: preguntar no exige aportarlos.
   Preguntar si tiene videos de referencia opcionales y si quiere mostrarlos en
   pantalla dividida/PiP o usarlos solo como guia de estilo. Recibir archivo/carpeta
   y registrar el uso; no insertar un ejemplo de estilo. Ver
   [videos de referencia](references/recursos.md#videos-de-referencia-y-composiciones-simultaneas).
   Preguntar tambien si quiere musica: ninguna, archivos MP3/audio o carpeta de
   canciones. Leer [documentos de apoyo](references/documentos-apoyo.md) para
   capturas fieles al HTML/CSS y [musica](references/musica.md) para la mezcla.
   Para Omni, no pedir presupuesto: usar el ciclo siguiente.
6. **Montaje y validacion.** Guardar elecciones en ENCARGO.md, mostrar TAREAS.md por
   video, analizar, editar y revisar. Dar proyecto, timeline/revision y pasos reales
   para REPRODUCIR cada montaje. Esperar el visto bueno antes del export final;
   si pide ajustes, volver a mostrar la revision afectada.
7. **Exportacion y publicacion opcional.** Tras la validacion preguntar si desea
   solo los archivos o publicarlos directamente en TikTok, YouTube, Facebook e
   Instagram, y en cuales cuentas. Titulo y descripcion los aporta el usuario
   en el brief o en ese momento: reutilizar lo escrito y pedir solo lo que falta.
   Exportar y verificar todos los videos aprobados. Publicar solo con autorizacion
   del contenido/destinos concretos y conexion comprobada; seguir
   [publicacion](references/publicacion.md). No confundir archivo exportado con post publicado.

No hacer todas las preguntas de instalacion y produccion de golpe. Agrupar
preguntas relacionadas, avanzar por etapas y guardar el siguiente paso para reinicios.
Si ya esta configurado, retomar desde materiales; una comprobacion tecnica breve
no obliga a repetir la instalacion.

## Omni: generar, mostrar y esperar

Omni recibe una pieza con imagen y voz YA CORREGIDAS y revisadas. Primero limpiar
el tramo, verificar palabras completas y sincronizacion, y preparar su entrada
con el informe de revision. No enviar la grabacion bruta ni restaurar despues
su audio sin limpiar: conservar la voz corregida de esa misma pieza. Este orden
tambien aplica a una muestra o prueba de angulo. Ver [Omni](references/omni.md).

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

Gestionar **TAREAS.md como registro vivo de cada cambio del video**, ademas de las
etapas generales. Antes de ejecutar un cambio autorizado, anotarlo con ID, video,
revision/tramo, accion y criterio de comprobacion. Marcarlo en curso al comenzar,
en revision al aplicarlo y hecho [x] SOLO despues de revisar el resultado real,
anotando evidencia. Actualizar el documento tras cada cambio, no reconstruirlo
al final. Incluir nuevas peticiones y defectos hallados; conservar historial y
reabrir tareas si una correccion posterior invalida lo hecho. Mostrar su ruta
absoluta y el avance durante el trabajo. Seguir [registro de cambios](references/continuidad.md#registro-vivo-de-cambios-en-tareasmd).
Actualizar este documento no requiere una nueva confirmacion del usuario ni
autoriza acciones pendientes. Cada salida lleva tareas propias identificables.

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
- [Documentos de apoyo](references/documentos-apoyo.md): HTML/CSS fiel, PDF,
  capturas y resaltados sincronizados con el discurso; material opcional.
- [Musica](references/musica.md): archivos/carpeta opcionales y voz corregida en off.
- [Publicacion](references/publicacion.md): reproduccion y visto bueno antes de
  exportar; textos del usuario, acceso y envio opcional a cuatro redes.
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
