# Conversacion ordenada: instalar, recibir, producir

Leer al comenzar o retomar un encargo. El orden de esta referencia sustituye la
antigua obligacion de pedir guion para las pruebas tecnicas de instalacion.
Preguntar solo lo que falta; una respuesta previa sigue siendo valida para el
encargo. Nunca pedir claves en el chat. Usar lista de tareas visible y guardar estado.

## A. Instalacion

1. Al invocar la skill, preguntar: «¿Ya tienes DaVinci Resolve instalado y el
   puente configurado, o necesitas que los instalemos?». Reutilizar una respuesta
   que ya conste; no repetirla durante el mismo encargo. Distinguir instalado de
   solo tener el instalador descargado, y puente instalado de puente activo.
   Si dice que si, comprobar brevemente la conexion existente. Si la conexion responde y
   Gemini esta configurado, pasar directamente a B o a las tareas pendientes del
   encargo; no pedir reinstalar, reiniciar ni activar un puente que ya responde.
   Si solo esta apagado, guiar su activacion. Si dice que no, iniciar la instalacion
   de los componentes que falten; si tiene solo una parte, conservarla. Un fallo
   de conexion por si solo no demuestra que falte la instalacion.
   Cuando falte el dato, preguntar version/edicion de Resolve, o revisarla localmente.
   Ante desconocimiento y acceso al equipo, ejecutar diagnostico local; no mandar
   al usuario a buscar algo que la IA puede leer. Si ya esta detectado, informarlo.
   Sin acceso local, seguir el modo guiado de instalacion.md: pedir solo sistema,
   arquitectura y version/edicion pendientes. Dar una recomendacion concreta con
   enlace oficial y pasos manuales, sin afirmar que se inspecciono el ordenador.
2. Elegir la via compatible leyendo instalacion.md. Si falta o requiere cambio,
   presentar version/edicion, descarga oficial y motivo. Preguntar por instalar
   esa version concreta, reutilizando autorizacion ya dada. Antes de cambiar una
   instalacion existente, resolver los proyectos que deban conservarse.
3. Instalar/reutilizar el MCP y registrarlo para el asistente real (Codex o Claude
   Code). Distinguir skill instalada, MCP registrado y conexion real. Conservar
   otros servidores, rutas y configuraciones. No reinstalar Resolve solo por un
   fallo de registro del cliente.
4. Gemini: si no hay una clave local configurada, preguntar si tiene una API key
   de Google AI Studio. Si falta, guiar a [AI Studio](https://aistudio.google.com/api-keys).
   Si existe, abrir la entrada local oculta de configure-gemini.ps1; no solicitar
   pegarla en el chat. En otro sistema usar el almacen local apropiado. Reutilizar
   una clave vigente. Ver gemini.md para verificar SDK, autenticacion y modelo.
5. Solo si falta activar la conexion, dar estos pasos al usuario, de forma numerada:
   abrir Resolve si esta cerrado; abrir o crear un proyecto si no hay uno; ir a Workspace > Scripts >
   resolve_bridge; mantener Resolve abierto y avisar «listo». Si se usa Studio con
   scripting directo, indicar su configuracion aplicable en lugar del puente.
   Reiniciar solo si un cambio de configuracion lo requiere; conservar el trabajo abierto.
6. Cuando responda, comprobar version y proyecto mediante la conexion. Si falta
   un paso, decir app, accion y resultado esperado. Guardar evidencia sin secretos.
   Las pruebas de autenticacion, catalogo, texto minimo y consulta de version/proyecto
   pueden ejecutarse sin guion ni brief; no analizar ni generar medios durante ellas.

Al completarse, decir brevemente «La conexion esta lista» solo si fue verificada y
PASAR DIRECTAMENTE a la recepcion. No terminar con «avisame cuando quieras editar».
En una instalacion ya operativa, omitir pasos completados y revisar solo la conexion
necesaria. Si queda un bloqueo externo, puede adelantarse la recepcion local sin
marcar la instalacion como terminada.

## B. Materiales y cantidad

Inventariar archivos de la carpeta actual con intake.py inventory. No explorar todo
el disco ni subir archivos. Por defecto no entrar a subcarpetas: si son parte del
material, acordar el alcance y usar --recursive.

- Si hay videos: mostrar lista numerada con nombres y preguntar «¿Usamos todos
  estos videos o solo algunos? Indica cuales». Aunque solo haya uno, confirmar
  que es el material elegido, salvo que el usuario ya lo haya indicado.
- Si no hay videos: «¿Cual es la ruta de la carpeta con tus videos?». Revisar la
  ruta recibida y preguntar todos o cuales. No pedir ruta si ya la proporciono.
- «¿Cuantos videos finales quieres obtener?». Diferenciar videos exportados de
  escenas Omni. Si quiere varios, concretar si son uno por archivo, recortes
  tematicos o versiones distintas y que materiales forman cada salida.
- Pedir audios, musica, logo o referencias opcionales. No bloquear por falta de
  audio separado: puede usarse la pista del video. No anadir musica por defecto.
- Preguntar la duracion media objetivo o intervalo de cada salida si no consta.
  La elige el usuario; no imponer un resumen corto. Si el material limpio no puede
  llegar con coherencia y calidad, explicar el maximo viable y esperar su decision.

## C. Documentos, siempre con rutas para el usuario

Inicializar la carpeta del encargo fuera del paquete y ejecutar workflow.py documents.
Devuelve rutas ABSOLUTAS existentes. Mostrarlas como enlaces locales clicables
si el cliente lo permite; tambien puede abrirse el archivo en el editor disponible.

Primero el brief:
«¿Quieres aportar un brief tecnico o usar el profesional por defecto? Puedes
leer y editar el predeterminado aqui: enlace absoluto a BRIEF-TECNICO.md».
Construir el enlace con la ruta devuelta por documents, nunca enviar ese texto
descriptivo en lugar de la ruta.

Luego el guion:
«¿Tienes un guion propio o usamos nuestro guion profesional por defecto? Puedes
leerlo y editarlo aqui: enlace absoluto a GUION-POR-DEFECTO.md».
SIEMPRE proporcionar la ruta, incluso si ya dijo «hazlo con el de defecto»;
en ese caso afirmar la eleccion y continuar, sin repetir la pregunta.

Si dice que no tiene guion, activar el profesional por defecto usando esa respuesta
real. No exigir redactar uno ni obligar a confirmar una segunda vez. Si pide uno
personalizado nuevo, preparar un borrador y confirmarlo. Nunca interpretar una
respuesta aun pendiente como una eleccion.

Las copias locales son editables. Si el usuario modifica la copia predeterminada
antes de elegirla, use-default-script usa su contenido. Tras activarla, mostrar
GUION-CREATIVO.md como ruta de trabajo vigente. Leer ambos documentos completos.
Para un documento propio, conservar su fuente y copiarlo al documento de trabajo
sin destruir la version anterior. Registrar confirm-brief y confirm-script (o
use-default-script) con las respuestas reales. «Ambos por defecto» basta para ambos.
Editar despues invalida el hash: revisar el cambio y registrar la instruccion real
del usuario para usarlo, sin reinstalar ni repetir toda la recepcion.

## D. Omni, imagenes, documentos y musica opcionales

Preguntar «¿Quieres generar escenas con otros angulos mediante Omni?» con opciones:
no; si, propon escenas adecuadas. Si elige si, registrar esa respuesta para UNA
generacion con omni-next; no preguntar presupuesto, tope ni cantidad de intentos.
Concretar el fragmento que se enviara a Google dentro del alcance ya acordado.
La eleccion habilita el recurso, no el uso de la grabacion bruta: antes de generar,
corregir y revisar imagen y voz del tramo, y preparar esa pieza con su informe.
Al mostrar el resultado, usar la voz ya corregida de la entrada. Ver omni.md.
Mostrar cada resultado y su coste disponible; preguntar si lo conserva, desea
ajustarlo/reintentarlo, generar otra escena o detener Omni. Esperar la respuesta
antes de volver a gastar. Conservar la toma por si solo no autoriza otra llamada.
Si elige no, omitir Omni y usar planos aportados o reencuadres con nitidez suficiente.

Preguntar «¿Quieres imagenes de apoyo? ¿Tienes HTML con su CSS, PDF, documentos o
presentaciones que quieras mostrar? Puedes pasar los archivos o su carpeta».
HTML y documentos son opcionales; si no tiene, seguir. Mostrar opciones:

- Sin imagenes nuevas, solo video.
- Usar imagenes que aporte el usuario.
- Usar capturas de sus HTML/PDF/documentos conservando su apariencia original.
- Generar imagenes: fotografia/representacion realista; ilustracion; diagramas o
  infografias; estilo de marca o una mezcla indicada por el usuario.

Para generar, mostrar SOLO vias disponibles: ImageGen nativo si el host lo tiene;
helper OpenAI Images con clave propia si se elige; otro proveedor ya conectado
solo si se comprueba su capacidad. Informar de lo que necesita configurarse sin
fingir que Claude tiene las herramientas de Codex. La eleccion de estilo no es un
permiso ilimitado de gasto. Cada recurso generado debe aparecer una sola vez.

Se pueden combinar documentos aportados e imagenes generadas. Abrir los HTML,
comprobar su CSS y capturar su aspecto real; insertar pasajes por su relacion con
el discurso corregido, con resaltados o sombreado legible cuando ayuden. Seguir
[documentos de apoyo](documentos-apoyo.md); no reemplazar su diseno por texto generico.

Preguntar «¿Quieres musica de fondo? Puedes pasar un MP3, indicar la carpeta de
canciones o continuar sin musica». Si aporta carpeta, reutilizar su eleccion o
preguntar si tiene una pista concreta o delega la seleccion. Seguir [musica](musica.md).
La pregunta es obligatoria; la musica es opcional y no exige una API de pago.

Preguntar tambien si tiene un video que quiera referenciar dentro del montaje o
solo como ejemplo de estilo. Puede pasar archivo/carpeta o continuar sin el.
Si quiere mostrarlo, ofrecer pantalla dividida, un video pequeno sobre el grande
(PiP) o eleccion de la IA segun el guion. Seguir
[videos de referencia](recursos.md#videos-de-referencia-y-composiciones-simultaneas).
Una referencia de estilo no debe insertarse por error como material de apoyo.

## E. Guardar el encargo y continuar

El asistente registra las respuestas en un JSON local (no pedir al usuario que
escriba JSON) y usa intake.py save. Campos:

```json
{
  "videos": ["ruta-absoluta-al-video-elegido.mp4"],
  "audios": [],
  "support_files": [],
  "reference_videos": [],
  "music": {"mode": "none", "files": []},
  "output_count": 1,
  "omni": false,
  "images": "none",
  "image_style": "no aplica",
  "user_responses": ["respuesta real que define el encargo"]
}
```

Sustituir las rutas de ejemplo por archivos reales. Para varias salidas, agregar
outputs con tantos elementos como output_count; cada uno tiene id unico, purpose
y videos (subconjunto de rutas elegidas). images admite none, provided, native y
openai-api. Para otro proveedor, adaptar el registro de forma explicita con sus
capacidades verificadas antes de producir; no etiquetarlo como uno distinto.
support_files guarda rutas absolutas de imagenes/HTML/PDF/documentos seleccionados.
reference_videos guarda objetos con path absoluto al video y use: on_screen o
style segun la respuesta real. Puede quedar vacio; no exigir videos adicionales.
La composicion y el momento de aparicion se concretan en guion/RECURSOS.md.
music.mode admite none, provided o undecided; provided requiere music.files con
audios elegidos. undecided es una pregunta pendiente, no una eleccion silenciosa.
Los audios de voz siguen en audios. El inventario detecta tipos; no renderiza HTML.
Opcionalmente cada output puede llevar publication con title y description que
el usuario escribio en su brief. Esos textos no autorizan publicar; si faltan se
piden al cierre, y si no se publicara no bloquean la edicion.

```text
python <skill>/scripts/intake.py inventory --directory <carpeta-materiales>
python <skill>/scripts/intake.py save --project-dir <encargo> --answers <respuestas.json>
```

ENCARGO.md conserva seleccion, numero y objetivos de las salidas, documentos y
elecciones de recursos. No habilita subidas ni generaciones ilimitadas por si solo. No exige
otra confirmacion global si las preguntas ya quedaron respondidas.
Continuar con gate, analisis, tabla de montaje y TAREAS.md por cada salida. Aplicar
el brief durante TODA la produccion y comprobar sus criterios al revisar cada export.
Si se piden tres videos, completar y entregar tres; un clip Omni no cuenta como un
video final. Reutilizar analisis ya valido cuando sirva a varias salidas sin repetir gasto.

## F. Mostrar, validar y entregar

Antes de presentarlo como listo, seguir [calidad](calidad.md): observacion neutra
de Gemini del discurso completo, controles locales y revision posterior del agente.
Escuchar/ver cada resultado automatico y el montaje completo; documentar la
revision y comprobar quality_review.py gate. Repetir sobre el export final.

Al terminar cada montaje, indicar como reproducirlo, con proyecto y timeline/revision
reales. Esperar el visto bueno y atender cambios antes de exportar como final.
Tras validar, preguntar si quiere solo los archivos o publicacion directa en las
redes elegidas. Recuperar titulo/descripcion del brief o pedirlos en ese momento.
Reutilizar respuestas completas sin otra confirmacion redundante. Seguir
[publicacion](publicacion.md) para acceso, textos exactos, autorizacion y estados.
Este cierre es una excepcion expresa a reglas antiguas que limiten las preguntas
al inicio: nunca omitir la validacion o publicar por haber terminado la edicion.
