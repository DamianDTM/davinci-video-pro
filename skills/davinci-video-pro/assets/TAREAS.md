# Tareas del encargo

Estados: pendiente, en curso, en revision, hecho con evidencia, bloqueado,
no aplicable con motivo. Reutilizar respuestas y pasos comprobados.

## Registro vivo de cambios por video

La IA mantiene aqui una tarea concreta por cada cambio previsto o solicitado,
ademas de la lista general de etapas que sigue. Anadirla ANTES de ejecutar,
actualizarla al empezar y marcar [x] solo despues de aplicar y revisar el resultado.
Mientras falte ejecucion o revision, mantener [ ] y el estado correspondiente.

Cada tarea indica: ID unico, video/salida, revision y tramo o alcance global,
origen (guion, brief, comentario del usuario o hallazgo), accion concreta,
criterio de comprobacion, estado, resultado y evidencia. Añadir fecha de actualizacion.
Usar subtareas cuando haya varios cambios que puedan completarse por separado.
No inventar tareas terminadas, tiempos del video ni rutas de evidencias.

Agregar los cambios reales del encargo debajo de este texto, agrupados por video.
Las tareas nuevas permanecen pendientes; despues de cada operacion se actualiza
su avance y resultado. Registrar tambien bloqueos y correcciones fallidas.
No cerrar en lote al terminar la sesion. Reabrir una tarea si cambia el requisito
o se descubre un defecto, conservando la revision y evidencia anteriores.

Al retomar otro chat, leer este registro y continuar los pendientes. Conservar
las notas y tareas existentes al incorporar esta seccion a un proyecto antiguo.
Una tarea hecha acredita el cambio revisado por la IA; no sustituye el visto
bueno del usuario para exportar ni su autorizacion para publicar.

## Instalacion y conexion

- [ ] Preguntar si ya tiene Resolve instalado y puente configurado; reutilizar respuesta previa y comprobar estado/version.
- [ ] Si ya funciona, omitir instalacion y pasar a materiales o pendientes; si esta apagado, activar el puente existente.
- [ ] Sin acceso local, pedir datos pendientes y dar version compatible, enlace oficial y pasos manuales.
- [ ] Reutilizar lo compatible o acordar una instalacion concreta preservando proyectos.
- [ ] Instalar/registrar solo componentes ausentes en el cliente elegido; reutilizar MCP y puente existentes, conservando ajustes.
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
- [ ] Abrir HTML con CSS y capturarlo; renderizar documentos aportados y revisar fidelidad visual.
- [ ] Vincular cada captura con su pagina/seccion, frase y tiempos del discurso corregido; no forzar insertos.
- [ ] Aplicar el brief: ruido, niveles, silencios, tartamudeos y repeticiones corregibles.
- [ ] Escuchar empalmes, conservar palabras completas, respiracion y significado.
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
- [ ] Dar proyecto, timeline/revision y como reproducir CADA video para validarlo.
- [ ] Registrar el visto bueno del usuario; mostrar de nuevo las revisiones con cambios antes del export final.
- [ ] Exportar y verificar MP4 completo, proyecto con medios y SRT.
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
