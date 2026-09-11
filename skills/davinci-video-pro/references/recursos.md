# Imágenes y clips adicionales

Antes de cualquier llamada, pedir el guion y pasar workflow.py gate. Pedir la preferencia de generación durante la recepción. Si el usuario ya pidió
imágenes acompañantes, generarlas dentro de ese alcance. Para clips de pago,
concretar duración, cantidad y presupuesto antes de gastar créditos.

Planificar primero una lista por inserto: frase, representación, formato, duración,
estilo, origen, estado y archivo final. Cada recurso generado será distinto.
Mantener prompts y procedencia en RECURSOS.md. Verificar que los archivos descargados
sean medios válidos antes de importarlos.

Usar ImageGen si está disponible y encaja con fotografías/ilustraciones. Inspeccionar
el resultado, respetar el aspecto de salida y dejar espacio para subtítulos.
Para gráficos de texto o diagramas simples, una composición nativa editable puede
resultar más precisa que una imagen generada.

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
