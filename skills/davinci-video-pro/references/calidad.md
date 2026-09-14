# Control automatico y revision obligatoria de la IA

Leer al analizar, preparar cortes, aplicar procesos automaticos y revisar cada
salida. Ningun resultado de un script, MCP, Gemini, transcriptor o generador se
aprueba solo por devolver success. La IA debe abrir/ver/escuchar lo pertinente,
compararlo con el material real y comprobar su aplicacion dentro del montaje.
No inventar observaciones ni rellenar casillas en lote. Si no puede reproducir
audio o inspeccionar imagen, dejar esa comprobacion pendiente y explicar el limite;
no afirmar cero errores. Una transcripcion correcta no demuestra un empalme natural.

## Analisis creativo y observacion neutra

1. Planificar con `gemini_video.py analyze`, guion y brief vigentes.
2. Para la revision del discurso usar `gemini_video.py verify` sobre la revision
   real completa; ante una duda puede observar ademas un fragmento con contexto
   suficiente. El helper valida guion/brief localmente,
   pero no envia sus textos, una transcripcion esperada ni el defecto supuesto.
   Mantiene muletillas y repeticiones en vez de corregirlas al transcribir.
3. La IA escucha el resultado y compara ambas evidencias. Ante discrepancia,
   escuchar fuente y export alrededor del corte, revisar forma de onda y, si
   hace falta, usar alineacion local de palabras. No cortar por voto de modelos,
   umbral de energia ni tiempos aproximados. No fijar temperatura 0 para cualquier
   modelo. Reutilizar analisis vigentes; una correccion tipografica no necesita
   volver a subir el video a Google.

Los tiempos de verify son relativos al archivo enviado, no a su original largo.
Registrar el inicio del fragmento para convertir coordenadas. No enviar todos los
subclips por defecto: revisar localmente primero y solicitar observacion externa
solo dentro de la autorizacion existente y cuando aporte evidencia necesaria.

## Cortes suaves sin mutilar el discurso

- Ubicar limites de palabras por escucha y forma de onda; preservar ataques,
  finales, respiraciones utiles, entonacion y pausas expresivas. Margen segun el
  contexto: 80–200 ms no es una regla obligatoria ni debe recuperar un error cortado.
- Para audio, comenzar con un microfundido corto, por ejemplo 5–20 ms, solo donde
  haya margen limpio. Ajustarlo escuchando. Si existe ambiente discontinuo, usar
  ambiente compatible de esa misma grabacion. No duplicar consonantes, superponer
  palabras, producir bajadas audibles ni aplicar un fundido que se coma el ataque.
- Un crossfade requiere material disponible en ambos extremos. Verificar esos
  handles antes de usarlo. Mantener las posiciones del montaje y la duracion
  acordada: no acortar audio por concatenacion con overlap sin compensar el video.
- En voz a camara, un corte limpio motivado por gesto/reencuadre o cubierto por un
  recurso pertinente suele funcionar mejor que disolver dos posiciones del rostro.
  Usar fundidos visuales breves en insertos; ajustar duracion a fps y movimiento.
  Revisar inicio, punto medio y final del fundido. Sin flashes, negros ni doble cara.
- Tras modificar un corte, volver a escuchar su entorno a velocidad normal y
  reproducir la frase completa. Revisar otra vez el audio despues de subtitulos,
  musica, Omni o procesos de reduccion de ruido. Evaluar artefactos metalicos,
  bombeo, respiraciones artificiales, saltos de timbre y sincronizacion.

## Evidencias locales por revision

Usar el Python del entorno de `requirements-media.txt`. Se necesita PyAV, NumPy,
Pillow y FFmpeg mediante imageio-ffmpeg. Las pruebas sinteticas no llaman APIs.

Crear una previsualizacion local identificada como tal para el control de calidad.
Eso no sustituye el visto bueno del usuario antes de exportar el final. Preparar
un plan JSON por salida con los valores reales acordados y el inventario de cortes.
Ejemplo de estructura, NO valores predeterminados de duracion o contenido:

```json
{
  "version": 1,
  "expected": {"frames": 90, "fps": "30/1", "width": 1080, "height": 1920, "audio": true, "speech": true},
  "cuts": [30, 60],
  "primary_video_spans": [{"start": 0, "end": 30}, {"start": 30, "end": 60}, {"start": 60, "end": 90}]
}
```

`cuts` enumera todos los empalmes internos de voz/imagen relevantes en fotogramas
de destino desde el inicio de la salida; se suman los de distintas pistas, sin
duplicados. Una lista vacia significa que realmente no hay empalmes internos.
`primary_video_spans` se obtiene leyendo los items reales de Resolve DESPUES de
montar; restar el inicio de timeline. Incluir la union de pistas que aportan imagen,
no audio ni una pista auxiliar de titulos que ocultaria un hueco en el video base.
Estos rangos de DESTINO son `[start,end)`; no trasladar esa convencion a endFrame
de origen de AppendToTimeline. Medir duraciones reales y resolver diferencias de fps.
Un tramo negro expresamente solicitado puede quedar como hallazgo intencional.
Si el proyecto usa fps variable, conformar una salida de revision de fps constante
segun lo acordado antes de este control; no cambiar la velocidad del discurso.

```text
python <skill>/scripts/quality_review.py --project-dir <proyecto> scan --file <preview.mp4> --plan <plan-qa.json> --output-dir <qa/revision-01> --subtitles <subtitulos.srt> --neutral-report <verificacion-gemini.json> --evidence <analisis.json>
```

Se puede repetir `--evidence` para resultados automaticos: transcripcion neutra,
alineacion, audio procesado, imagen generada, captura de documento, reporte de
montaje o de transiciones. Registrar todas las operaciones en TAREAS.md; asociar
cada resultado a una evidencia revisable. Los archivos deben existir y no cambiar
durante QA. No adjuntar claves, variables de entorno ni registros con secretos.

Cuando haya discurso, --neutral-report es obligatorio y debe ser un informe
verify de Gemini del audio COMPLETO de la revision. El script rechaza analyze
como sustituto. La observacion neutra se revisa luego por la IA; son dos pasos.
Por defecto speech sigue el valor audio. Usar speech:false solo si realmente
no hay voz (p. ej., pieza musical); la IA debe comprobar esa decision en el plan.
Si Gemini no esta disponible, se puede continuar trabajo local independiente,
pero dejar esta revision pendiente; no marcarla como hecha ni ocultar el limite.

Una modificacion solo visual permite reutilizar un informe neutro anterior si
el archivo fuente aun existe con su hash original y el audio PCM decodificado
es IDENTICO (frecuencia, canales, disposicion, muestras y tiempos de la pista). Si cambia el audio o su codificacion
produce diferencias, requiere nueva observacion. La revision visual del agente
se repite siempre sobre la salida actual, incluso cuando se reutiliza Gemini.

El script decodifica todos los fotogramas, valida cantidad/resolucion/fps/tiempos,
presencia de audio y estructura temporal del SRT; mide sonoridad y pico real;
detecta candidatos a negro incluso de un fotograma y huecos del inventario real.
Conserva log de audio, capturas y clips de apertura, cierre y cada corte con
1,5 s de contexto por lado cuando exista. Son pistas para investigar, no una
certificacion de calidad. La longitud del contexto se amplia manualmente cuando
no permita entender la frase. No evalua automaticamente tartamudeos ni literalidad.

## Revision de la IA y puerta de entrega

1. Leer report.json y reproducir cada muestra; abrir capturas y evidencias de
   procesos automaticos. Comparar contra la fuente cuando corresponda. Escuchar y
   ver tambien el video COMPLETO: las capturas periodicas no cubren todo el contenido.
2. El script crea AI-REVIEW.json con TODO pendiente. Solo despues de observar,
   la IA anota agente/modelo, reproduccion completa real y una observacion concreta
   por item con rutas absolutas de evidencias existentes del reporte. No copiar
   una misma frase generica para todos ni usar otro script para aprobarlo en lote.
3. Para un item correcto usar verdict `pass`. Un warning solo se puede aceptar con
   `intentional`, explicando por que es intencional o un falso positivo observado.
   Los blockers no se exceptuan: corregir causa/plan segun el encargo y ejecutar
   scan en OTRA carpeta. Si no puede comprobarse algo, dejar `pending` y resolverlo.
4. Ejecutar:

```text
python <skill>/scripts/quality_review.py --project-dir <proyecto> gate --file <preview.mp4> --report <qa/revision-01/report.json> --ai-review <qa/revision-01/AI-REVIEW.json>
```

La puerta comprueba pendientes, evidencias y hashes del video, guion, brief,
plan e informes/capturas. Cambiar cualquiera invalida esa revision. Exige datos
de revision, pero no puede demostrar que una IA escucho: la obligacion es observar
realmente, no fabricar un JSON que pase. El agente conserva esa responsabilidad.

Pasar gate antes de presentar una version como lista, preparar material revisado
para Omni o entregar/publicar. En `prepare_clip.py`, usar el AI-REVIEW.json vigente
como --review-file despues de comprobar gate contra su --source. La extraccion
automatica tambien se ve y escucha antes de enviar a Omni. La misma exigencia
de revision aplica a cada transformacion automatica posterior.

Mostrar al usuario como reproducir la previsualizacion en Resolve o el archivo
local. Esperar su visto bueno. Despues exportar el final y aplicar scan/revision/gate
a ESE archivo: la revision del preview no aprueba un export diferente. Ante nuevos
defectos, corregir, revisar y mostrar el cambio al usuario. Ningun estado de QA
autoriza por si solo exportar o publicar en redes. Guardar las rutas finales y
los pendientes reales por cada salida, sin prometer cero errores.
