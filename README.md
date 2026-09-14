# DaVinci Video Pro 2.4.0

Skill para **Codex local y Claude Code** que guia la instalacion y organiza un
encargo de edicion profesional con DaVinci Resolve, Gemini y recursos opcionales.

Repositorio: [DamianDTM/davinci-video-pro](https://github.com/DamianDTM/davinci-video-pro).
Paquete de esta version: [version 2.4.0](https://github.com/DamianDTM/davinci-video-pro/releases/tag/v2.4.0).

## Instalacion sencilla

Copia esto en Codex local o Claude Code:

> Instala o actualiza DaVinci Video Pro desde https://github.com/DamianDTM/davinci-video-pro,
> Lee el README y aplica la skill para el asistente que estoy usando.
> Primero configura la conexion y despues guiame por materiales, cantidad de videos,
> brief tecnico, guion y recursos. Muestrame las rutas editables de los documentos.

El asistente descarga/clona esa version o descomprime su ZIP y usa Python >=3.11:

```text
python install.py --client codex
python install.py --client claude-code
```

Para actualizar, agregar --update al comando del cliente: conserva respaldo de la
skill anterior y no reemplaza proyectos ni preferencias. --client both se usa
solo si se pide instalar para ambos. La carpeta portable es skills/davinci-video-pro.
El instalador copia la skill; no instala Resolve ni llama APIs por si solo.

Invocacion: $davinci-video-pro en Codex o /davinci-video-pro en Claude Code.
Si no aparece, recargar o abrir otra sesion. Un chat web aislado no controla el
Resolve local por recibir un enlace: requiere acceso local, scripts y MCP compatibles.

## Que preguntara y hara

1. **Resolve:** si ya esta instalado y su version/edicion. Si no lo sabes, lo
   detecta. Si falta o debe cambiarse, propone una version compatible concreta
   y pregunta por instalarla, preservando proyectos y autorizaciones anteriores.
2. **Conexion:** registra el MCP para tu cliente, configura/reutiliza tu API key
   propia de Google mediante entrada local oculta, explica como abrir Resolve,
   un proyecto y activar el puente, y comprueba la conexion.
3. **Materiales:** revisa la carpeta actual. Si hay videos, muestra una lista y
   pregunta si usa todos o cuales; si no hay, pide la ruta. Recibe audio opcional.
4. **Resultados:** pregunta cuantos videos finales quieres, su duracion objetivo y como distribuir
   los materiales entre ellos.
5. **Brief tecnico:** pregunta propio o predeterminado, muestra su ruta absoluta
   editable y lo lee completo. Es obligatorio durante la edicion y la revision.
6. **Guion:** pregunta propio o predeterminado y SIEMPRE muestra la ruta para
   leerlo o editarlo. Si no tienes uno, usa nuestro guion profesional.
   **«Hazlo con el de defecto» basta para seguir**, sin otra confirmacion.
7. **Recursos opcionales:** pregunta por escenas Omni, imagenes y HTML/CSS, PDF,
   documentos o presentaciones aportados como archivos/carpeta. Ofrece generacion
   de imagenes con las herramientas disponibles. Pregunta tambien si quieres
   musica desde MP3/otro audio, una carpeta de canciones o ninguna.
8. **Produccion y revision:** guarda ENCARGO.md y tareas por salida, analiza,
   monta y corrige. Te indica como abrir y reproducir cada montaje en Resolve
   y espera tu visto bueno antes de exportarlo como final.
9. **Entrega y publicacion opcional:** pregunta si quieres solo archivos o tambien
   publicarlos directamente en TikTok, YouTube, Facebook e Instagram, en las
   cuentas elegidas. Usa el titulo y descripcion que escribiste en el brief o
   te los pide al terminar. Publica el contenido autorizado con acceso real,
   verifica cada destino y entrega sus enlaces/estado, ademas de los exports.

Si ya respondiste algo, lo reutiliza. No termina la instalacion pidiendote que
inicies otro encargo: continua directamente con la recepcion.

Si el asistente no puede revisar tu equipo, sigue en modo guiado: pregunta solo
sistema/arquitectura y datos pendientes, recomienda una version concreta, entrega
el enlace oficial y explica cada paso que debas realizar. La
[guia de instalacion](skills/davinci-video-pro/references/instalacion.md) incluye
el formulario de Resolve Free 21.0.3 para Windows como referencia comprobada.
Sin navegador, identifica la fecha de comprobacion del enlace; no simula una
verificacion actual. Para controlar Resolve necesita acceso real al equipo.

## Omni sin pregunta de presupuesto

Al elegir Omni, primero limpia y revisa la imagen y la voz del tramo elegido.
Genera desde esa pieza corregida, restaura su voz ya limpia y te muestra el video
y su coste disponible. No envia la grabacion bruta con los tartamudeos ni vuelve
a poner su audio sin corregir. prepare_clip.py requiere --review-file con la
revision del agente; el helper de Omni verifica los archivos y sus hashes antes
de acceder a claves o Google. Ese registro no reemplaza escuchar y revisar.
Espera a que lo revises y decidas si conservarlo, ajustar/reintentar, generar otra
escena o parar. No pide presupuesto ni genera varias opciones mientras esperas.
Conservar una toma no autoriza una generacion adicional.

Guarda el historial en GASTOS-OMNI.md y distingue estimaciones, subtotales parciales
y costes desconocidos. La API devuelve uso, no un recibo: no presenta una cifra
estimada como importe pagado. No hay reintentos automaticos tras un fallo.
Este ciclo se aplica en Codex y Claude Code, tambien al retomar otro chat.

## Nuestros documentos predeterminados

Los HTML se abren y capturan con su CSS, fuentes y recursos: importa su aspecto
y su informacion. PDF y documentos se renderizan para conservar su diagramacion.
Los insertos se eligen por su relacion con lo que dice el hablante, con resaltados
o sombreado de lectura sincronizados. La voz corregida puede seguir en off sobre
esas imagenes. Aportar estos recursos es opcional; se pregunta sin exigirlos.
Ver [documentos de apoyo](skills/davinci-video-pro/references/documentos-apoyo.md).

La musica tambien es opcional: archivos/carpeta del usuario, con fundidos y nivel
por debajo de la voz. No instala ni consume APIs musicales por defecto.

- [Guion profesional](skills/davinci-video-pro/assets/GUION-POR-DEFECTO.md):
  apertura, contexto, desarrollo, demostracion y cierre; planos, recursos y CTA
  fieles a lo pronunciado.
- [Brief tecnico](skills/davinci-video-pro/assets/BRIEF-TECNICO.md):
  ruido, niveles de voz, silencios accidentales, tartamudeos y repeticiones
  corregibles, palabras completas, subtitulos blancos con palabras clave doradas
  mas grandes, titulares altos, recursos sin repetir, fundidos, color y QA del export.

Proceden del montaje profesional y de sus mejoras confirmadas. No contienen el
discurso, las rutas ni los medios personales de aquel video. Se crean copias
editables en la carpeta del encargo; el asistente muestra sus rutas locales reales.
Si editas la copia predeterminada antes de elegirla, se usa tu contenido editado.
Despues se trabaja en GUION-CREATIVO.md y BRIEF-TECNICO.md.

El guion dirige mensaje/apariencia; el brief es un requisito tecnico obligatorio.
Los helpers de produccion comprueban que ambos esten elegidos y vigentes.
Las pruebas tecnicas de conexion pueden realizarse antes: no dependen del guion.
Esta excepcion no permite analizar archivos, generar recursos o editar sin los
documentos, ni autoriza subir material o gastar sin el alcance acordado.

## Continuidad

La [guia de publicacion](skills/davinci-video-pro/references/publicacion.md)
incluye la validacion previa, textos del usuario y registro por red. Instalar
la skill no conecta redes ni incluye un servicio de autopublicacion. Se usa una
integracion autorizada o navegador disponible, comprobando cuenta y permisos.
Si falta acceso, entrega los MP4, textos y pasos manuales con publicacion pendiente.
Una subida, borrador o publicacion privada no se presentan como un post publico.
El titulo/descripcion pueden darse al cierre; no bloquean editar ni obligan a publicar.

Cada encargo tiene su carpeta y registra seleccion, cantidad de salidas y recursos
en ENCARGO.md. Un encargo puede producir varios videos, con montajes y exports
identificables. Los comentarios se resumen por guion/brief y alcance; tras tu
confirmacion se actualizan ambos con historial. Las preferencias generales viven
en ~/.davinci-video-pro/templates o DAVINCI_VIDEO_PRO_HOME y sobreviven a actualizaciones.

Nuevo chat: «Continua mi encargo leyendo el estado guardado».
Otro video: «Quiero editar otro video; usa mis preferencias y el guion por defecto».
Siempre se muestran las rutas de los documentos y se piden solo los datos pendientes.

## Alcance y comprobaciones

Ruta de referencia: Windows, Resolve Free 21.0.3.7 y MCP Samuel Gursky 2.224.1.
El asistente verifica compatibilidad actual y reutiliza instalaciones funcionales.
Gemini 3.8 Flash es el modelo preferido de comprension; Omni 1.1 Flash, para
perspectivas sintetizadas, con revision y coste visible por generacion. Los modelos requieren
acceso real de la cuenta. Codex puede usar ImageGen nativo; Claude usa recursos
aportados o un proveedor de imagenes conectado/configurado con su clave propia.

Ver [VALIDACION.md](VALIDACION.md). Las pruebas de esta version son locales con
servicios simulados y material sintetico. No garantizan ediciones sin errores:
el asistente debe escuchar y revisar cada salida aplicando el brief.
«Connected» en el cliente MCP no prueba por si solo que Resolve responda.
macOS/Linux, Claude Desktop/Cowork y una instalacion desde cero en otro equipo
requieren comprobacion en ese destino.

No incluye claves, creditos, medios personales ni instaladores propietarios.
Las claves se introducen localmente; analisis y generacion pueden consumir cuota.

Fuentes: [Skills Codex](https://learn.chatgpt.com/docs/build-skills),
[Skills Claude](https://code.claude.com/docs/en/skills),
[MCP Resolve](https://github.com/samuelgursky/davinci-resolve-mcp).
