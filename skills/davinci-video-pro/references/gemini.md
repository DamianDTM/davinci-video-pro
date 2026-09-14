# Gemini para comprender el material

Configurar y probar la conexion antes de la recepcion del encargo; no requiere
guion ni brief. Para analizar archivos, ambos documentos elegidos y vigentes son
obligatorios y debe pasar workflow.py gate. Preferido: gemini-3.8-flash. Comprobar acceso
y modalidad reales; no sustituir un modelo sin explicar el cambio al usuario.

Cada usuario aporta GEMINI_API_KEY de Google AI Studio. No pegarla en el chat.
En Windows ejecutar configure-gemini.ps1 con -WorkDirectory <proyecto> y
-PythonExecutable <python>. El formulario no requiere guion, oculta la clave,
verifica el catalogo de Google y guarda la variable del usuario. -ValidateOnly
comprueba parametros locales sin abrir el formulario ni llamar a Google.
Es una variable local, no una boveda cifrada. En otros sistemas configurar una
variable o almacen de secretos del usuario sin imprimir su valor.

Instalar google-genai==2.22.0 en un entorno aislado: esa version fue probada.
Consultar documentacion oficial antes de cambiarla. No registrar entornos completos.
El helper comprueba la version antes de construir el cliente. Si detecta otra o
falta el SDK, indica el comando de instalacion en ese entorno, sin llamar a Google.
El pin corresponde al SDK de Python, no al modelo Gemini 3.8. Interactions usa
configuracion interna para impedir reintentos; no asumir compatibilidad con otras
versiones. Las pruebas que necesitan el SDK exacto se omiten con un mensaje claro
si no esta disponible; una omision no significa que esa integracion haya pasado.

```text
python <skill>/scripts/gemini_video.py --project-dir <proyecto> status
python <skill>/scripts/gemini_video.py --project-dir <proyecto> models
python <skill>/scripts/gemini_video.py --project-dir <proyecto> check --model gemini-3.8-flash
python <skill>/scripts/gemini_video.py --project-dir <proyecto> analyze --file <archivo> --output <informe-nuevo.json> --model gemini-3.8-flash --processing agentic --upload-to-google
python <skill>/scripts/gemini_video.py --project-dir <proyecto> verify --file <revision-o-fragmento> --output <verificacion-nueva.json> --model gemini-3.8-flash --processing static --upload-to-google
```

status es local; models/check son pruebas tecnicas sin guion. analyze exige
guion y brief tecnico vigentes antes de crear cliente o leer claves. check usa una
respuesta minima de texto y no demuestra analisis audiovisual. La autenticacion sola no autoriza subir
archivos: explicar que los materiales elegidos se envian a Google, reutilizar
autorizacion si ya se dio y concretar el alcance si falta.

El helper incluye el guion como fuente principal y el brief tecnico en la peticion,
registra hashes y modelo, espera Files ACTIVE y elimina su entrada remota en finally.
Si falla limpieza, informar. Tiempos de Gemini son estimados: verificar con escucha,
forma de onda y transcripcion alineada antes de cortar. No inventar dialogo faltante.

Lo anterior describe analyze. verify mantiene los requisitos locales de guion y
brief, pero NO envia sus textos, nombres de archivos descriptivos ni la respuesta
esperada. Transcribe lo escuchado, incluidos tropiezos. La IA debe revisar el
resultado contra el audio real; ver [calidad](calidad.md). No certifica cortes ni
precision temporal. No usar analyze para decidir si desaparecio un defecto ya
descrito en el brief. Cada informe registra mode y editorial_context_sent.

El SDK conserva reintentos desactivados. SOLO analyze/verify disponen de una capa
limitada para HTTP 500/502/503/504: --max-attempts 1, 2 (predeterminado) o 3, incluida
la peticion inicial, con espera creciente corta. Sin reintentar 400/401/403/429,
timeouts, errores desconocidos, subida o JSON invalido. Guarda .attempts.json
tambien en fallos; el coste incierto no se presenta como cero. Reutilizar la misma
subida durante esos intentos y revisar el registro antes de iniciar otra llamada.
Omni NO usa esa capa; conserva exactamente un intento por decision del usuario.

Agentic sirve para explorar el material segun el encargo; static es configurable
para clips cortos o compatibilidad. Registrar cual ocurrio, no solo cual se pidio.
Reutilizar informes por hash del video, guion, brief tecnico y modelo. No repetir analisis externo
para una revision solo tipografica. Ante 401/403/429 clasificar causa y no reintentar
indefinidamente; no activar facturacion ni cambiar cuentas por su cuenta.

Fuentes: [Video](https://ai.google.dev/gemini-api/docs/video-understanding),
[SDK](https://github.com/googleapis/python-genai),
[Files](https://ai.google.dev/gemini-api/docs/files).
