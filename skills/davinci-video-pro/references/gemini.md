# Gemini para comprender el material

Primero pedir y registrar el guion; workflow.py gate debe pasar incluso antes de
probar credenciales o listar modelos. Preferido: gemini-3.8-flash. Comprobar acceso
y modalidad reales; no sustituir un modelo sin explicar el cambio al usuario.

Cada usuario aporta GEMINI_API_KEY de Google AI Studio. No pegarla en el chat.
En Windows ejecutar configure-gemini.ps1 con -WorkDirectory <proyecto> y
-PythonExecutable <python>. El formulario verifica la puerta antes de abrirse y
antes de consultar Google, oculta la clave y guarda la variable del usuario.
Es una variable local, no una boveda cifrada. En otros sistemas configurar una
variable o almacen de secretos del usuario sin imprimir su valor.

Instalar google-genai==2.22.0 en un entorno aislado: esa version fue probada.
Consultar documentacion oficial antes de cambiarla. No registrar entornos completos.

```text
python <skill>/scripts/gemini_video.py --project-dir <proyecto> status
python <skill>/scripts/gemini_video.py --project-dir <proyecto> models
python <skill>/scripts/gemini_video.py --project-dir <proyecto> check --model gemini-3.8-flash
python <skill>/scripts/gemini_video.py --project-dir <proyecto> analyze --file <archivo> --output <informe-nuevo.json> --model gemini-3.8-flash --processing agentic --upload-to-google
```

status es local; models/check/analyze exigen guion confirmado. check comprueba
texto y no demuestra analisis audiovisual. La autenticacion sola no autoriza subir
archivos: explicar que los materiales elegidos se envian a Google, reutilizar
autorizacion si ya se dio y concretar el alcance si falta.

El helper incluye el guion como fuente principal y el brief tecnico en la peticion,
registra hashes y modelo, espera Files ACTIVE y elimina su entrada remota en finally.
Si falla limpieza, informar. Tiempos de Gemini son estimados: verificar con escucha,
forma de onda y transcripcion alineada antes de cortar. No inventar dialogo faltante.

Agentic sirve para explorar el material segun el encargo; static es configurable
para clips cortos o compatibilidad. Registrar cual ocurrio, no solo cual se pidio.
Reutilizar informes por hash del video, guion y modelo. No repetir analisis externo
para una revision solo tipografica. Ante 401/403/429 clasificar causa y no reintentar
indefinidamente; no activar facturacion ni cambiar cuentas por su cuenta.

Fuentes: [Video](https://ai.google.dev/gemini-api/docs/video-understanding),
[SDK](https://github.com/googleapis/python-genai),
[Files](https://ai.google.dev/gemini-api/docs/files).
