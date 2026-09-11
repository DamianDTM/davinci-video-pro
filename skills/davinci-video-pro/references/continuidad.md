# Guion, revisiones y preferencias entre chats

Python >=3.11. Estos comandos solo operan archivos locales. Resolver rutas absolutas.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> init
python <skill>/scripts/workflow.py --project-dir <proyecto> status
```

init no sobrescribe proyectos. Crea los dos documentos, carpetas, tareas, estado,
comentarios pendientes y AGENTS.md/CLAUDE.md para orientar nuevos chats.
Si hay documentos previos sin estado, elegir otra carpeta y conservar los existentes.
Las plantillas se guardan en DAVINCI_VIDEO_PRO_HOME o ~/.davinci-video-pro/templates.
Codex y Claude comparten ese lugar. Un nuevo proyecto hereda estilo, pero necesita
elegir guion (propio o predeterminado) y autorizaciones vigentes. Otro equipo necesita una copia de las plantillas.

## Guion primero

Si el usuario dice «usa el guion por defecto» o una eleccion equivalente, ejecutar:

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> use-default-script --confirmation <respuesta-real>
python <skill>/scripts/workflow.py --project-dir <proyecto> gate
```

La frase del usuario confirma la eleccion; NO volver a preguntar. Se activa el
guion profesional del paquete, con las preferencias del perfil, y se conserva el
brief tecnico del proyecto. El asistente lee ambos y continua con las fases
pendientes. No se inventan autorizaciones de envio/gasto. Un chat posterior con
gate vigente retoma sin pedir de nuevo el guion. Una eleccion para otro video se
registra en la carpeta de ese video. No sobrescribir un guion propio existente.

Guardar el guion real en GUION-CREATIVO.md, conservando su texto fuente. Si es un
borrador, mostrarlo y confirmarlo. --confirmation contiene la respuesta REAL del
usuario que entrega el guion para usarlo o confirma el borrador; nunca fabricarla.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> confirm-script --confirmation <respuesta-real>
python <skill>/scripts/workflow.py --project-dir <proyecto> gate
```

La puerta verifica el hash vigente y rechaza plantillas sin completar. Cambiar el
guion directamente invalida la confirmacion. Una revision confirmada actualiza
el hash. Pedir confirmacion de un borrador no requiere volver a pedir un guion ya entregado.

## Rondas de comentarios

Guardar cambios en CAMBIOS-PENDIENTES.md mientras se ejecutan las ediciones ya
autorizadas. Preparar dos documentos candidatos y un resumen que separe cambios
del video actual de preferencias generales. No consolidar preferencias antes de
confirmar el resumen. No generalizar nombres, discursos, marcas o CTA concretos.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> stage-revision --creative <guion-candidato.md> --technical <brief-candidato.md> --summary-file <resumen.md>
```

Mostrar el resumen y preguntar «¿Es correcto este resumen?». Esperar respuesta.
Si hay correcciones, archivar el pending y preparar otra propuesta; no confirmar
una obsoleta. Para preferencias futuras agregar --profile-creative y
--profile-technical con dos plantillas generales. Conservar PENDIENTE_DE_GUION
en la plantilla creativa: un nuevo video requiere la eleccion de su guion.
Conservar la seccion «Preferencias creativas reutilizables»: use-default-script
incorpora ese bloque confirmado al guion base. Las preferencias tecnicas se
heredan en BRIEF-TECNICO.md. Las actualizaciones del paquete no pisan ese perfil.

```text
python <skill>/scripts/workflow.py --project-dir <proyecto> apply-revision --confirmation <respuesta-real>
```

Se comprueban cambios concurrentes, se archivan los originales en history y se
actualizan ambos documentos y el perfil si estaba incluido. Cada documento recibe
solo cambios pertinentes; no inventar modificaciones para forzar una diferencia.
Guardar tareas y proximo paso. Una propuesta preparada no equivale a confirmada.

Si existe transaction.json tras una interrupcion, no llamar APIs: leer su historial
y restaurar los documentos y project-before.json, o completar la revision
comprobando los archivos y el resumen. Conservar evidencia hasta verificar.

Casos de comportamiento: instalar sin guion pide guion antes de pruebas; guion
entregado se reutiliza; nuevo chat lee estado; nuevo video hereda estilo y pide
contenido o acepta el guion por defecto; cambios se resumen y confirman antes de persistir como preferencias.
