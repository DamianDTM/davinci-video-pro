# Elegir una via compatible antes de montar

Guia practica para evitar ensayos repetidos. Verificar version/edicion reales y
capacidades del MCP instalado. Un nombre presente o un resultado True no prueba
el efecto: leer de vuelta y revisar imagen/audio del render. Mantener un registro
de que funciono en este equipo; no usar intentos fallidos como reglas universales.

| Operacion | Restriccion observada | Via y verificacion |
|---|---|---|
| Conectar Free | El puente funciono en 21.0.3.7; 21.1 cambio el soporte Python. | Seguir instalacion.md. No actualizar Free ni comprar Studio automaticamente. |
| Transcripcion/subtitulos desde audio | Las funciones nativas relevantes requieren Studio; devuelven exito, no una lista fiable de palabras por si solas. | Usar Gemini y, cuando aporte valor y este disponible, alineacion/transcripcion local. Escuchar cortes; Studio no elimina esa tarea. |
| SRT y estilo de la pista subtitle | El API examinado no expone importacion directa ni edicion completa del texto/estilo. | Importar por UI si hay acceso, o usar Text+ editable. Entregar SRT auxiliar. No declarar todo texto imposible de editar. |
| Text+ en posicion/duracion exactas | InsertFusionTitleIntoTimeline recibe el nombre; no acepta parametros arbitrarios de pista o tiempo. | Crear una timeline por bloque de titulo, configurar Text+ y colocar la timeline anidada mediante su MediaPoolItem. Seguir resolve-practico.md y probar un titulo antes del lote. |
| Stills, duraciones y huecos | Puede haber defaults de 150 frames o redondeo segun medios/fps. | Leer GetStart/GetEnd/GetDuration de cada item. Comprobar cobertura real. No asumir endFrame exclusivo ni sumar un frame siempre. |
| Ganancia por parametro | Volume/SetProperty no ofrece ese control en la version examinada. | Preset Fairlight comprobado, UI o copia de audio procesada localmente y reimportada. Revisar niveles, ruido y sincronizacion. |
| Fundidos/transiciones/normalizacion | SetFades, AddTransition y NormalizeAudioLevel aparecen en 21.1; la presencia depende del host. | Antes de 21.1, usar Fusion, pistas solapadas, audio procesado o UI compatibles. Comprobar handles, duracion y resultado real. |
| Render | Algunas combinaciones de preset/valores se rechazan; no hay lectura completa de GetRenderSettings. | Partir de preset conocido y validar claves por separado. AudioCodec, VideoQuality y ExportVideo son nombres documentados, no opciones universalmente prohibidas. Verificar el archivo con QA. |
| Cache tras reemplazar archivos | Sobrescribir puede dejar metadatos o render antiguo. | Versionar recursos con nuevo nombre cuando ocurra, reimportar y verificar; no sobrescribir originales. |

Fuentes para actualizar esta tabla: README de scripting instalado con Resolve,
[limitaciones del MCP](https://github.com/samuelgursky/davinci-resolve-mcp/blob/main/docs/reference/api-limitations.md),
[registro de versiones](https://github.com/samuelgursky/davinci-resolve-mcp/blob/main/src/utils/resolve_versions.py).
Se basa en la revision de 14-09-2026; no promete soporte de versiones futuras.
