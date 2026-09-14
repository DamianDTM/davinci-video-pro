# Tareas del encargo

Estados: pendiente, en curso, hecho con evidencia, no aplicable con motivo.
Reutilizar respuestas y pasos comprobados. Anotar evidencia y siguiente paso.

## Instalacion y conexion

- [ ] Preguntar si posee Resolve y version/edicion; si no sabe, detectar localmente.
- [ ] Sin acceso local, pedir datos pendientes y dar version compatible, enlace oficial y pasos manuales.
- [ ] Reutilizar lo compatible o acordar una instalacion concreta preservando proyectos.
- [ ] Instalar/registrar el MCP en el cliente elegido y conservar otros ajustes.
- [ ] Configurar o reutilizar API key Google mediante entrada local oculta.
- [ ] Verificar autenticacion/modelo sin enviar videos; no requiere guion.
- [ ] Indicar abrir Resolve, abrir proyecto y activar Workspace > Scripts > resolve_bridge si aplica.
- [ ] Verificar respuesta real de Resolve y guardar estado de configuracion.

## Recepcion despues de conectar

- [ ] Inventariar la carpeta actual o pedir la ruta de videos si no hay material.
- [ ] Preguntar todos o cuales; registrar la seleccion y audios/referencias opcionales.
- [ ] Preguntar cantidad de videos finales y como distribuir materiales entre ellos.
- [ ] Registrar la duracion objetivo elegida por el usuario para cada video.
- [ ] Preguntar brief propio/default y mostrar SIEMPRE su ruta absoluta editable.
- [ ] Leer el brief completo y registrar su eleccion real; es obligatorio.
- [ ] Preguntar guion propio/default y mostrar SIEMPRE la ruta editable del predeterminado.
- [ ] Si no tiene guion o pide el de defecto, activarlo sin otra confirmacion.
- [ ] Preguntar si se generaran escenas Omni.
- [ ] Preguntar si se usaran/generaran imagenes y mostrar opciones de estilo/proveedor disponibles.
- [ ] Preguntar por HTML/CSS, PDF y documentos opcionales; recibir archivos/carpeta y registrar seleccion.
- [ ] Preguntar por videos de referencia opcionales: mostrar en pantalla o solo estilo; recibir archivo/carpeta.
- [ ] Si se mostraran, registrar pantalla dividida/PiP o composicion delegada y tramo del guion.
- [ ] Preguntar musica opcional: MP3/archivo, carpeta de canciones o ninguna; registrar pistas/seleccion delegada.
- [ ] Guardar ENCARGO.md, concretar archivos enviados y gasto si corresponde.
- [ ] Comprobar guion y brief vigentes mediante workflow.py gate.

## Produccion: repetir y documentar para CADA video final

- [ ] Analizar material seleccionado con Gemini, guion y brief; verificar tiempos localmente.
- [ ] Crear tabla de montaje y criterios del brief para esta salida.
- [ ] Probar capacidades de titulos/audio/fundidos en una muestra antes de automatizar el lote.
- [ ] Registrar cada proceso automatico y la evidencia que la IA abrira/escuchara para revisarlo.
- [ ] Abrir HTML con CSS y capturarlo; renderizar documentos aportados y revisar fidelidad visual.
- [ ] Vincular cada captura con su pagina/seccion, frase y tiempos del discurso corregido; no forzar insertos.
- [ ] Aplicar el brief: ruido, niveles, silencios, tartamudeos y repeticiones corregibles.
- [ ] Escuchar empalmes, conservar palabras completas, respiracion y significado.
- [ ] Revisar microfundidos y cortes visuales sin doble rostro, flashes ni cambios de sincronizacion.
- [ ] Obtener observacion neutra de Gemini del discurso completo y contrastarla por escucha de la IA; registrar desacuerdos.
- [ ] Antes de Omni, preparar imagen y voz sincronizadas desde el tramo YA CORREGIDO; registrar la revision con prepare_clip.py --review-file.
- [ ] Crear solo recursos elegidos; imagenes unicas y una escena Omni por turno de revision.
- [ ] Restaurar la voz corregida de la entrada y revisar la toma Omni antes de mostrarla; no recuperar el audio bruto.
- [ ] Mostrar cada video Omni y su coste disponible; guardar GASTOS-OMNI.md, sin pedir presupuesto.
- [ ] Esperar decision del usuario antes de otra generacion o reintento Omni.
- [ ] Aplicar subtitulos, enfasis, CTA, titulares, transiciones, audio y color.
- [ ] Animar resaltados de documentos cuando ayuden; conservar la voz corregida en off sobre los recursos.
- [ ] Revisar pantalla dividida/PiP elegida: proporciones, margenes, subtitulos y una voz principal clara.
- [ ] Mezclar solo la musica elegida con fundidos y voz clara; marcar no aplicable si no se pidio.
- [ ] Revisar TODO el montaje contra guion y brief; registrar defectos y pendientes.
- [ ] Leer la cobertura real de Resolve y ejecutar quality_review.py scan con plan, SRT y evidencias automaticas.
- [ ] La IA reproduce TODO, escucha cada empalme, abre capturas/evidencias y documenta AI-REVIEW.json por item.
- [ ] Resolver hallazgos y pasar quality_review.py gate sobre esta previsualizacion; no autoaprobar pendientes.
- [ ] Dar proyecto, timeline/revision y como reproducir CADA video para validarlo.
- [ ] Registrar el visto bueno del usuario; mostrar de nuevo las revisiones con cambios antes del export final.
- [ ] Exportar y verificar MP4 completo, proyecto con medios y SRT.
- [ ] Repetir QA y revision de la IA sobre el export final; comprobar gate y hashes antes de entregar/publicar.
- [ ] Registrar id de salida, ruta absoluta, revision y evidencia de QA.

## Publicacion opcional al terminar

- [ ] Preguntar si desea solo archivos o publicacion directa en TikTok/YouTube/Facebook/Instagram; registrar redes elegidas.
- [ ] Recuperar titulo y descripcion del brief o pedirlos al usuario; no inventar contenido para publicar.
- [ ] Comprobar acceso, cuenta exacta y visibilidad por destino; mostrar contenido y registrar autorizacion vigente.
- [ ] Publicar solo exports validados y autorizados con conexion real; guardar id/estado y evitar reintentos duplicados.
- [ ] Verificar publicacion y entregar enlace por destino, o archivos/textos y pasos si queda pendiente.

## Cierre

- [ ] Resumir comentarios por documento y alcance; preguntar si es correcto.
- [ ] Tras respuesta, actualizar guion, brief y preferencias correspondientes con historial.
- [ ] Comprobar que el numero de videos completos entregados coincide con ENCARGO.md.
- [ ] Entregar enlaces/rutas de TODOS los exports y guardar estado para otro chat.
