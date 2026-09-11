# Edición profesional

## Recepción

Pedir el guion ANTES de configurar mediante APIs o editar. Comprobar workflow.py gate y luego recibir los materiales. Reutilizar lo que
ya se haya proporcionado. Pedir rutas o archivos con un mensaje normal; no pedir
subidas mediante una herramienta que solo admite respuestas de texto.

Recoger en pocas preguntas:
- Guion, mensaje central, público, plataforma, formato y duración objetivo.
- Videos, tomas alternativas, audio separado/voz en off, música, logo y marca.
  El audio separado es opcional; si solo hay video, revisar su pista original.
- Generación: solo material aportado, imágenes ilustrativas, o también clips
  adicionales. Para generación de pago, proveedor y límite de créditos/presupuesto.
- Preferencias que se aparten del estilo base; contenido que no debe recortarse.

Mantener GUION-CREATIVO.md como fuente principal y BRIEF-TECNICO.md como criterios de ejecucion; leer continuidad.md para confirmar revisiones. Completar ambos desde las plantillas y completar un inventario con ruta,
duración, resolución, fps, audio, hash y función de cada archivo. No inventar
duraciones, tomas o diálogos que aún no se han revisado.

## Plan y lista de tareas

Mostrar la lista de configuración y producción, con realizado/en curso/pendiente
o no aplicable justificado. Marcar por resultados, no por comandos lanzados.
Registrar cada nueva petición y cómo se verificará. Ante "cuánto falta", indicar
fase y trabajo pendiente; dar una estimación solo si hay datos para sustentarla.

Tabla de montaje por segmentos:
origen/in/out, texto conservado, motivo del corte, tiempo de destino, encuadre,
recurso único, subtítulo/énfasis, transición y audio.
Trabajar en fotogramas de la línea de tiempo; distinguir fps de origen y destino.
Para fps variable o mezcla de tasas, verificar conformado y sincronía.

## Montaje

- Preservar originales; crear una línea de tiempo propia con nombre de revisión.
- Quitar preparación, salida, silencios accidentales, muletillas reiteradas,
  sílabas repetidas, reinicios y frases fallidas. Mantener pausas expresivas,
  respiración útil, intención y personalidad. No recortar automáticamente toda pausa.
- Conservar la versión completa de una autocorrección. No alterar hechos para
  fingir que el presentador dijo otra cosa. Lo irreparable se señala para nueva toma.
- Escuchar alrededor de cada empalme y usar microfundidos cuando haga falta.
  Mantener consonantes completas, timbre y ruido de fondo continuos.
- Variar encuadres con zoom y desplazamientos moderados. Un recorte de una cámara
  no crea una perspectiva auténtica. No deformar rostro/manos ni exagerar zoom.
- Elegir recursos por frase. Un recurso generado aparece una sola vez:
  zoom, recorte y recolor del mismo archivo no constituyen un recurso nuevo.
- Usar fundidos breves en imágenes y clips de apoyo. Como punto de partida,
  unos 8 fotogramas a 30 fps; adaptar al ritmo. Solapar en pistas si hace falta
  para evitar un destello del presentador entre dos recursos.
- Ajustar exposición y color con moderación. Voz clara y uniforme; si hay música,
  bajarla bajo el diálogo, comprobar derechos y conservar el carácter del mensaje.

## Subtítulos y llamadas

Subtitular todo el discurso con frases breves, normalmente 1–2 líneas.
Comprobar ortografía, nombres, sincronía y términos según el audio real.
Mantener texto editable en Resolve; el SRT contiene texto y tiempos, no WordArt.

Estilo base para 1080 × 1920:
- Texto blanco Segoe UI Bold, nominal 68 px.
- Conceptos fundamentales en dorado, Segoe UI Black Italic, nominal 84 px.
- Contorno oscuro fino para legibilidad. Sustituir la familia por una instalada
  equivalente cuando corresponda, declarando el cambio.
- Recalcular anchuras, espaciado, saltos y posición al mezclar tamaños; alinear
  la línea base. Reducir proporcionalmente las frases largas y comprobar margen.
- Usar una paleta consistente. No convertir todas las palabras en énfasis.
- Subtítulos en zona inferior legible sin tapar el rostro ni las interfaces del destino.
  Colocar el titular superior alto con margen; 115 px desde arriba fue adecuado
  para el clip original, pero se debe adaptar a la composición y plataforma.

Cuando el discurso pida comentar o escribir, mostrar una llamada animada sincronizada
con la acción y la palabra realmente pronunciada. Mantenerla legible unos segundos,
con un icono discreto cuando ayude. No inventar promesas ni palabras para comentar.

## Revisión y exportación

Primero revisar en Resolve una muestra representativa de título, subtítulo mixto,
frase larga, inserto, fundido y CTA. Exportar una revisión nueva y comprobar:
- Archivo reproducible, duración y fotogramas esperados, resolución/fps correctos.
- Audio presente, sincronía, principio/final de palabras y empalmes naturales.
- Ausencia de cuadros negros, huecos, offline o recortes inesperados.
- Todos los subtítulos renderizados, sin solapamientos, con énfasis y buena lectura.
- Cada recurso pertinente aparece una vez y las transiciones funcionan realmente.
- Los requisitos del guion, incluidos los añadidos durante la edición, están cubiertos.

Para cambios solo visuales sobre un audio ya revisado, comparar el audio decodificado
con la revisión anterior y revisar las imágenes afectadas. No repetir análisis externo
costoso sin necesidad. Para cambios de discurso, volver a escuchar cortes y sincronía.

Exportación habitual: MP4 H.264 + AAC, dimensión y fps acordados; preservar el original
cuando no se especificó formato. Verificar la configuración aceptada por Resolve.
Entregar MP4, DRP y preferentemente DRA/ZIP con medios, SRT, guion creativo y brief tecnico finales.
Comprobar que el archivo de proyecto incluye recursos de Fusion/Loader y fuentes
o instrucciones de sustitución. No prometer portabilidad por exportar un DRP solo.

Cerrar la lista de tareas y dar la ruta absoluta exacta del video más reciente,
enlace para abrirlo y ruta del proyecto. No publicar ni enviar a terceros por defecto.


## Angulos y revisiones

Seguir omni.md para perspectivas sintetizadas y restaurar siempre el audio original.
Al cerrar comentarios, resumir cambios por documento y alcance, preguntar si son
correctos y esperar confirmacion antes de aplicar revisiones persistentes.
