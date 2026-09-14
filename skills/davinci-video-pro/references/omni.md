# Perspectivas alternativas con Omni

Solo generar si el usuario eligio Omni. Requiere guion y brief tecnico vigentes;
comprobar workflow.py gate y reutilizar las elecciones ya dadas. Modelo preferido:
gemini-omni-1.1-flash. Es una perspectiva sintetizada plausible; puede cambiar
labios, manos, rostro o fondo. No garantiza una segunda camara ni sincronizacion exacta.

Planificar en el guion fragmentos pertinentes de cuatro segundos a 720p y cambios
moderados de 30–45 grados. Mantener identidad, ropa, decorado y dialogo original.
No forzar una toma en cada escena. La cantidad de videos finales no equivale a
una autorizacion para generar esa cantidad de tomas Omni automaticamente.

## Primero corregir la pieza de entrada

Antes de llamar a Omni, limpiar el tramo elegido: silencios accidentales, ruido,
tartamudeos, reinicios y repeticiones involuntarias. Aplicar los mismos cortes a
imagen y voz, conservar palabras completas y revisar empalmes y sincronizacion.
Exportar una pieza intermedia desde ese montaje corregido. Basta preparar el
tramo elegido; no hace falta terminar todos los videos ni los subtitulos.

Omni debe recibir la imagen Y EL AUDIO de esa pieza, nunca la grabacion inicial
con los errores. Pedir en el prompt que quite los errores no reemplaza limpiarlos
antes. Mantener visible al presentador; preparar la base sin subtitulos ni recursos
superpuestos que puedan ser reinterpretados por la generacion.

La IA escribe un informe local de la revision realizada: pieza y tramo revisados,
correcciones aplicadas, resultado de la escucha/reproduccion y sincronizacion.
No es una pregunta adicional al usuario. Pasarlo a prepare_clip.py con
--review-file. El helper conserva los hashes de montaje, fragmento, informe,
guion y brief; omni_video.py rechaza una entrada sin registro vigente antes de
leer claves, subirla o consumir el intento. Es un control de trazabilidad:
no certifica por si solo que la voz este libre de errores; revisar de verdad.
Si cambia el montaje o el fragmento, revisar otra vez y preparar un registro nuevo.

## Un intento y una decision cada vez

NO preguntar presupuesto, tope de gasto ni numero maximo de intentos. La respuesta
real que elige Omni habilita UNA generacion; no pedir una segunda confirmacion
si ya se conoce el fragmento y esta acordado enviarlo a Google. Registrar esa
misma respuesta con omni-next. Nunca inventar una respuesta ni tratar la espera
como permiso. Conservar cualquier limite que el usuario establezca expresamente.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> omni-next --confirmation <respuesta-real-que-elige-Omni>
python <skill>/scripts/prepare_clip.py --project-dir <proyecto> --source <montaje-audiovisual-corregido.mp4> --review-file <revision-del-montaje.md> --start <segundos-del-montaje-corregido> --output <fragmento-corregido-nuevo.mp4>
python <skill>/scripts/omni_video.py --project-dir <proyecto> --file <fragmento-corregido-nuevo.mp4> --scene angulo-01 --prompt-file <prompt.md> --upload-to-google
```

Tras cada intento, incluso si falla:

1. Mostrar el clip completo reproducible o abrirlo en el visor del cliente; dar
   tambien su ruta absoluta. Si fallo, explicar que no hay un resultado util.
2. Mostrar su coste disponible y enlazar GASTOS-OMNI.md. Indicar si es estimado,
   parcial, desconocido o confirmado con evidencia de facturacion.
3. Preguntar si quiere conservar la toma, ajustarla/reintentar, generar otra escena
   o parar Omni. Esperar su respuesta antes de otra llamada. La revision de la IA
   o la aprobacion de conservar la toma no sustituyen una peticion de generar otra.
4. Registrar la respuesta que pide continuar y la escena revisada. Usar otro id
   de escena para conservar el resultado y coste anteriores.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> omni-next --reviewed-scene angulo-01 --confirmation <respuesta-real-que-pide-otra-generacion>
```

Si pide repetir exactamente la misma peticion, agregar --retry-of angulo-01 a
omni-next. Solo despues de revisar ese resultado; nunca usarlo para saltar un
fallo automatico. El siguiente intento debe usar un identificador nuevo.
No generar lotes ni variantes de fondo mientras el usuario revisa. Puede continuar
trabajo local independiente, conservando como pendiente la decision sobre Omni.

El helper comprueba una autorizacion de un solo uso y conserva intentos, prompt,
hashes de guion/brief, uso, respuesta del usuario y costes entre chats. Los antiguos
omni-plan, --budget-usd y --estimated-usd ya no son necesarios ni se usan para Omni.
Un plan anterior no habilita un lote; al actualizar, mostrar el ultimo intento
existente y retomar desde la decision pendiente sin volver a pedir presupuesto.

## Costes transparentes

Interactions entrega tokens de uso, no un recibo en dolares. omni_costs.py calcula
una estimacion local y guarda la tarifa, fecha y fuente usadas. Consultar las
[tarifas oficiales](https://ai.google.dev/gemini-api/docs/pricing#gemini-omni-flash)
al ejecutar: si cambiaron, actualizar PRICING en el helper o marcar la estimacion
como pendiente de recalcular. La IA hace esta consulta; no pide un presupuesto
al usuario. No confundir Standard con Batch, promociones ni otros modelos.

Referencia verificada el 11-09-2026 para Omni 1.1 Flash Standard: entrada USD 1.50
por millon de tokens; salida de texto USD 9.00; salida de video USD 17.50.
A 720p, 5792 tokens por segundo de video. El helper usa los tokens devueltos;
si faltan, estima solo la salida de video a partir de la duracion del MP4 recibido.
Entrada, pensamiento u otros componentes ausentes/ambiguos quedan pendientes.
No sumar pensamiento dos veces ni considerar campos ausentes como cero.

Presentacion: «Video generado. Coste estimado: USD ... (subtotal parcial, si aplica).
Cargo confirmado por Google: pendiente. Aqui puedes revisar la toma».
Mostrar un total estimado solo si los componentes estan completos y conciliados.
Sin datos suficientes, decir «coste desconocido»; un timeout no significa coste cero.
El registro suma componentes conocidos e identifica intentos sin coste conocido;
no presentarlo como saldo, gasto total real ni limite de facturacion. No buscar
credenciales adicionales de facturacion ni comprar creditos para habilitar este flujo.

## Ejecucion, revision e integracion

Interactions genera un video de cuatro segundos, 720p, 9:16 o 16:9. Requiere PyAV.
En SDK 2.22.0 client_for desactiva los reintentos en el recurso Interactions;
la prueba HTTP 429 verifica una sola peticion. Volver a probar al cambiar el SDK.
No reenviar una solicitud incierta para averiguar si termino. Si queda omni.lock
por interrupcion, consultar ledger/proveedor antes de retirarlo; conservar evidencia.
Files se retira al finalizar incluso ante fallo. Si queda una copia, informar.

Revisar inicio, medio, final y reproduccion completa: apariencia, boca con la voz
ya corregida, manos, pizarra/textos, continuidad y nitidez. Comprobar que Omni no
introdujo nuevos tropiezos visuales o movimientos repetidos. Mostrar el resultado al
usuario aunque requiera ajustes. Solo integrar una toma que pase la revision;
si falla, explicar el limite y esperar su decision sobre otra generacion.

Conformar fps/resolucion y RESTAURAR LA VOZ YA CORREGIDA del fragmento enviado.
No recuperar el audio de la grabacion bruta ni conservar una voz regenerada que
reintroduzca tartamudeos. Hacer esta mezcla antes de mostrar la toma al usuario.
Preservar la posicion temporal del discurso corregido y cortar en limites de frases.
Si cambia su duracion despues de generar, revisar la sincronia antes de integrar;
no generar de nuevo sin una peticion del usuario. Crear una linea de tiempo nueva,
conservar subtitulos/transiciones y exportar el video completo solicitado.
Una comparativa o clip de prueba no reemplaza el montaje completo.

La prueba de origen produjo 720x1280/24fps y una perspectiva lateral clara, con
sincronia aproximada y cambios en pizarra. Aquella prueba uso el audio original;
el flujo vigente exige limpiarlo y revisarlo antes de generar, para no heredar errores.

Fuentes: [Omni](https://ai.google.dev/gemini-api/docs/omni),
[SDK Usage](https://github.com/googleapis/python-genai/blob/main/google/genai/_gaos/types/interactions/usage.py),
[Guia de prompts](https://deepmind.google/models/gemini-omni/prompt-guide/).
