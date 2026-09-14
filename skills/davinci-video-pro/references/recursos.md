# Imágenes y clips adicionales

Preguntar tambien por HTML/CSS, PDF, documentos y presentaciones aportados, todos
opcionales. Si existen, seguir [documentos de apoyo](documentos-apoyo.md) para
leer/renderizar, capturar fielmente su diseno y sincronizar insertos y resaltados.
Para canciones aportadas y voz en off, leer [musica](musica.md).

Antes de generar, comprobar que el usuario eligio imagenes en ENCARGO.md,
leer guion y brief tecnico vigentes y pasar workflow.py gate. No pedir documentos
ya elegidos. Mostrar estilos y vias disponibles segun flujo-guiado.md. Pedir la preferencia de generación durante la recepción. Si el usuario ya pidió
imágenes acompañantes, generarlas dentro de ese alcance. Para Omni seguir
[su ciclo de revision](omni.md): una generacion, mostrar video y coste, esperar
decision antes de otra; no pedir presupuesto. Con otros proveedores de clips,
concretar duracion, cantidad y alcance de gasto antes de consumir creditos.

Planificar primero una lista por inserto: frase, representación, formato, duración,
estilo, origen, estado y archivo final. Cada recurso generado será distinto.
Mantener prompts y procedencia en RECURSOS.md. Verificar que los archivos descargados
sean medios válidos antes de importarlos.

Usar ImageGen si está disponible y encaja con fotografías/ilustraciones. Inspeccionar
el resultado, respetar el aspecto de salida y dejar espacio para subtítulos.
Para gráficos de texto o diagramas simples, una composición nativa editable puede
resultar más precisa que una imagen generada.

## Videos de referencia y composiciones simultaneas

Preguntar durante la recepcion: «¿Tienes algun video que quieras mostrar como
referencia dentro del montaje, o usar solo como guia de estilo? Puedes pasar el
archivo o indicar su carpeta; tambien podemos continuar sin video de referencia».
Reutilizar la respuesta si ya consta. La pregunta debe contemplarse, aportar un
video es OPCIONAL y su ausencia no bloquea el encargo.

Si lo quiere mostrar, ofrecer pantalla dividida (ambos videos a la vez), PiP
(uno grande y otro pequeno superpuesto por un tramo) o dejar que la IA elija la
composicion segun el guion. No exigir un instante exacto: usar el momento pertinente
al discurso corregido salvo que el usuario indique uno. Conservar la eleccion en
guion/RECURSOS.md con fuente, tramo, composicion, tiempos de montaje y audio principal.

Registrar archivos locales elegidos en reference_videos de intake.py: cada entrada
tiene path absoluto y use: on_screen (puede aparecer) o style (solo inspira).
Una referencia style NO se inserta ni presta su audio, y no autoriza copiar su
contenido. Identificar que aspectos del ejemplo quiere seguir (ritmo, composicion,
tipografia, transiciones) sin reemplazar su guion. Si el papel del archivo es
ambiguo, preguntar antes de incorporarlo. No sumar referencias a la cantidad de
videos finales ni tratarlas como tomas principales que haya que usar por completo.

Para pantalla dividida/PiP, conservar proporciones y nitidez, jerarquia clara,
marcos/margenes coherentes y posiciones que no tapen rostros, documentos, CTA ni
subtitulos. Usar entradas y salidas suaves y duracion suficiente para entender
la relacion entre ambos planos; no mantener dos videos por adorno. Una unica
voz principal legible: silenciar o bajar el audio del inserto salvo que el usuario
quiera oirlo, en cuyo caso evitar dos discursos simultaneos. Mantener la voz
corregida en off y sincronizar los tiempos con el montaje depurado. Si el inserto
aporta dialogo que se va a escuchar, revisar tambien sus errores segun el brief.

Revisar la reproduccion de esa composicion y mostrarla dentro del montaje para
la validacion previa al export. La IA puede elegir detalles de composicion cuando
el usuario lo delega; no debe inventar que aporto un video ni forzar su presencia.

## Higgsfield opcional

"Highfield" probablemente se refiere a Higgsfield; usar ese nombre y comprobar la
identidad del proveedor si hay ambigüedad. No se utilizó ni se probó ese conector
en el video que originó esta skill. No es un requisito para configurar Resolve.

Descubrir primero si hay herramientas de Higgsfield ya conectadas. Si no, consultar
[su instalación oficial](https://higgsfield.ai/mcp) y los mecanismos de plugins/MCP
que permita el cliente del destinatario. No inventar herramientas ni parámetros,
y no afirmar que quedó instalado porque se guardó una URL.

Al 10-09-2026 el proveedor identifica https://mcp.higgsfield.ai/mcp como su conector
oficial. Verificarlo al configurar. Seguir su autenticación real con la cuenta del
usuario, consultar modelos/capacidades y presupuesto, y probar una consulta sin
generar antes de enviar el encargo concreto. No reutilizar OAuth ni credenciales
de otra persona, no comprar créditos automáticamente y no confundir suscripciones
web con acceso a una API.

Preparar prompt, duración, relación de aspecto y referencias; ejecutar solo las
generaciones acordadas. Esperar job completion, obtener el archivo mediante el
mecanismo admitido y comprobarlo. No llamar video a un PNG ni sustituir clips
solicitados por imágenes sin informar y acordar el cambio.

Si no hay conexión disponible, pedir al usuario que genere/exporte el clip desde
Higgsfield con el prompt preparado y que proporcione el archivo. Continuar el
montaje independiente sin dar por completado el recurso pendiente.

Fuentes:
[Superficies oficiales](https://higgsfield.ai/creator-hub/help-center/getting-started/official-higgsfield-platforms),
[API](https://docs.higgsfield.ai/).


## Codex y Claude

ImageGen de Codex no se transfiere a Claude. Si el host tiene generador nativo,
usar su herramienta y verificar el archivo. Si Claude no lo tiene, ofrecer conectar
un proveedor de imagenes (por ejemplo, API de OpenAI con clave propia) o recibir
imagenes del usuario. Preparar prompts desde el guion y explicar lo que falta.
No cambiar de proveedor ni subir referencias a otro servicio sin autorizacion.
No simular una imagen mediante un nombre de archivo ni marcar su tarea completa.

Para Claude sin herramienta nativa, esta incluido scripts/openai_image.py. Configurar
OPENAI_API_KEY en el entorno o variable del usuario de Windows, nunca en el chat.
Consultar modelo, acceso y tarifas actuales. El helper requiere modelo explicito,
guion confirmado y autorizacion de una imagen con estimacion/tope. Genera un PNG
desde un prompt; no sube referencias ni realiza ediciones de imagenes existentes.

```text
python <skill>/scripts/openai_image.py --project-dir <proyecto> --prompt-file <prompt.md> --output <imagen-nueva.png> --model <modelo-disponible> --confirmation <autorizacion-real> --estimated-usd <estimacion> --max-usd <tope-para-esta-imagen>
```

Una llamada por recurso, sin reintentos automaticos. El registro bloquea repetir
una solicitud con el mismo destino si hubo respuesta incierta. El tope se aplica
a la estimacion de esa imagen, no configura la facturacion del proveedor; llevar
el total acordado en RECURSOS.md. Revisar la imagen completa antes de importar.
Para referencias/ediciones usar una herramienta compatible y la documentacion
oficial vigente, con el mismo guion y alcance autorizado.

No se incluye clave ni creditos de OpenAI. Higgsfield sigue siendo opcional.
Fuente: [Imagenes OpenAI](https://developers.openai.com/api/docs/guides/image-generation).
