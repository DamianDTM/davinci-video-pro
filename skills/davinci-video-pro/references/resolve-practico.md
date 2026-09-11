# Notas operativas de Resolve

Observaciones empíricas del flujo Windows Free 21.0.3.7 + MCP 2.224.1.
Recomprobar en otra versión; no tratarlas como especificación universal.
Consultar Context7 y el README local de Scripting cuando cambie la API.

## Conexión y edición

Preferir las herramientas del MCP y leer sus esquemas. En Free con puente, un
script externo que usa scriptapp("Resolve") puede devolver None aunque el MCP
sí funcione. Para operaciones que no exponga una herramienta puede usarse el
cliente del checkout instalado:
```python
import sys
sys.path.insert(0, str(repo))
from src.utils.resolve_bridge_client import connect
resolve = connect(require_enabled=False, timeout=120)
project = resolve.GetProjectManager().GetCurrentProject()
```
No acceder al token directamente. No confundir consola externa con ejecución
dentro de Resolve. Mantener una sola operación que cambie la línea de tiempo,
la composición o el render a la vez.

Identificar proyecto/timeline por sus IDs guardados y verificar su nombre.
No seleccionar el primer proyecto o una pista por número fijo de otro montaje.
Guardar IDs y asociaciones de pistas en el estado del encargo.

## Duraciones e imágenes

Medir el resultado de AppendToTimeline. Se observó un desfase de un fotograma:
con endFrame=out-1 algunos medios devolvían duración esperada-1. Si ocurre,
borrar únicamente el item recién creado, sin ripple, y probar endFrame=out.
Comprobar duración y final global; no sumar uno indiscriminadamente.

Los stills ignoraron el recorte al insertarlos y duraron 150 frames. Funcionó
envolver el still en una timeline y recortar el clip anidado. Una duración
fragmentada contigua para mantener una imagen en pantalla no debe confundirse
con reutilizarla en un segundo inserto narrativo.

Para fundir un recurso anidado con transparencia: MediaIn como foreground de Merge,
Background con alpha 0 y Merge a MediaOut. Animar Blend con BezierSpline.
Para pasar entre recursos en pistas distintas, hacer el solapamiento suficiente
y evitar que se descubra el plano inferior. Capturar fotogramas intermedios.

## Text+ editable

Funcionaron títulos Text+ nativos por bloques, dentro de timelines anidadas, y
un nodo por palabra para controlar color, estilo, tamaño y colocación.
Segoe UI Bold y Black Italic estaban instaladas; comprobar la fuente real.

SetInput("Center", [x,y]) funcionó. Un diccionario con índices numéricos fue
convertido a claves de texto por el puente y dejó la posición sin cambios.
No bloquear la composición con comp.Lock mientras se cambia un título: se observó
una lectura correcta de parámetros pero un render que conservaba el texto anterior.
SetInput puede devolver None aunque haya funcionado; leer y renderizar.

Size equivalente a píxeles/640 fue una calibración local para esos títulos,
no una fórmula universal. Calibrar la salida real en la resolución de destino.
Medir anchuras de cada estilo y tamaño; los caracteres en cursiva pueden sobresalir.

En TextPlus, habilitar Enabled2 antes de consultar/configurar la segunda capa
de shading: sus campos aparecieron solo después. ElementShape2=1 fue contorno;
Thickness2 alrededor de 0.01–0.014 y RGB azul muy oscuro produjeron un borde sutil.
Las palabras fundamentales usaron Black Italic 84 px frente a Bold 68 px.
Mantener esta jerarquía como diseño adaptable, no como coordenadas universales.

## Render y entrega

timeline_frame capture con quality=frame, format=png dio imagen exacta de Resolve.
La miniatura no sirve para verificar una transición temporal. No capturar mientras
hay otro render. Un capture puede restablecer el rango de salida: reaplicar todas
las opciones de exportación final después.

Funcionó H.264 Master, mp4/H264, modo de clip único, MarkIn/MarkOut, dimensiones,
fps y AAC. En esta combinación SelectAllFrames=False y VideoQuality fueron
rechazados: comprobar parámetros individualmente y no afirmar un bitrate fijado
cuando quedó heredado del preset.

Comprobar JobStatus y el archivo real: decodificar, contar fotogramas, escuchar,
inspeccionar frames. AAC puede añadir una cola mínima respecto de la duración
de imagen; distinguir esa diferencia de un error de montaje.

ExportProject y ArchiveProject con medios dieron DRP y DRA utilizables.
Los Loader pueden conservar rutas absolutas; recopilar los archivos y documentar
relink si al restaurar en otro equipo lo necesitan. No alterar bases de datos
de bibliotecas ni usar edición binaria para solucionar una API sin consultarlo.
