# Perspectivas alternativas con Omni

Requiere guion entregado/confirmado y workflow.py gate. Modelo preferido
gemini-omni-1.1-flash, verificado en el flujo de origen. Es una sintesis de una
perspectiva plausible; puede cambiar labios, manos, rostro o fondo. No es una
segunda camara real ni garantiza sincronizacion exacta.

Planificar en el guion las escenas apropiadas. Como punto de partida, fragmentos
de cuatro segundos a 720p, con un cambio moderado de 30–45 grados. Cantidad segun
duracion/ritmo y presupuesto, no una toma forzada en cada escena. Mantener identidad,
ropa y decorado en el prompt, derivado de la escena aprobada. No inventar dialogo.

## Presupuesto y ejecucion

Consultar tarifas vigentes despues de la puerta del guion; concretar envio a
Google y plan de gasto. El helper reserva una estimacion por intento; esto NO es
un limite de facturacion del proveedor. Usar estimaciones conservadoras incluyendo
entrada, salida y margen. Si no se puede estimar, acordar un ensayo acotado.
No repetir solicitudes inciertas para comprobar si la primera se completo.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> omni-plan --max-attempts <cantidad> --budget-usd <tope-acordado> --confirmation <respuesta-real>
python <skill>/scripts/prepare_clip.py --project-dir <proyecto> --source <video> --start <segundos> --output <fragmento-nuevo.mp4>
python <skill>/scripts/omni_video.py --project-dir <proyecto> --file <fragmento-nuevo.mp4> --scene angulo-01 --prompt-file <prompt.md> --estimated-usd <estimacion-con-margen> --upload-to-google
```

El helper usa Interactions con salida video, cuatro segundos, 720p y 9:16 o 16:9.
En SDK 2.22.0 client_for desactiva el reintento en la configuracion del recurso
Interactions (strategy=none). El ajuste global se traduce de forma diferente ahi;
la prueba HTTP 429 verifica que no se reenvia. Volver a probar al cambiar el SDK.
Requiere PyAV para verificar la entrada. Guarda prompt, hash del guion, intento y
uso; rechaza escenas duplicadas y exceso del plan. No hay reintentos automaticos.
Files se retira al finalizar incluso ante fallo. Si queda una copia, informar.
Si queda omni.lock por interrupcion, revisar ledger/proveedor antes de retirarlo.

## Revision e integracion

Revisar cuadro a cuadro muestras de inicio, medio y final, mas reproduccion completa:
apariencia, boca con audio original, manos, pizarra/textos, continuidad y nitidez.
Una toma generada no se marca terminada hasta pasar esta revision. Si falla, usar
otra solucion permitida por el guion y explicar el limite; otra generacion requiere
estar dentro del alcance y presupuesto autorizado.

Conformar fps/resolucion a la linea de tiempo y RESTAURAR el audio del original.
Preservar posicion temporal del discurso. Preferir cortes en limites de frases.
Crear una linea de tiempo nueva, conservar subtitulos y transiciones del montaje,
exportar el video completo y comprobarlo. Una comparativa corta no reemplaza el
video completo cuando eso pidio el usuario.

La prueba de origen produjo 720x1280/24fps y una perspectiva lateral clara, con
sincronia aproximada y cambios en pizarra. Se uso el audio original al montar.

Fuentes: [Omni](https://ai.google.dev/gemini-api/docs/omni),
[Tarifas](https://ai.google.dev/gemini-api/docs/pricing#gemini-omni-flash),
[Guia de prompts](https://deepmind.google/models/gemini-omni/prompt-guide/).
