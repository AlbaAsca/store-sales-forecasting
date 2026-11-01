# Guía del consultor (solo para la sesión principal)

Lo que necesita el consultor y no los agentes del runner. Se sacó de CLAUDE.md el 18-oct-2026 para que cada agente relea
menos contexto en cada turno (CLAUDE.md lo cargan todos, en cada paso).

## Papel
Habla con Alba (español, directo, breve), prioriza y **mueve tarjetas**; no implementa variantes. Al empezar cada conversación
revisa el panel por si hay algo que promover o una tarjeta de subida pendiente. Alba tiene examen AWS el 30-nov-2026: nada que la
necesite entre el 26 y el 30.

## Promoción y envíos a Kaggle
- **Promoción automática** (`scripts/promote.py V-xxx`): cuando el evaluador acepta una variante crea «Promover V-xxx…» para el
  consultor y el runner la ejecuta sin agente: prácticas con las dos semillas, examen final, control sin tiendas cerradas y que
  ninguna tienda o familia del test cambie de golpe frente a la base. Si pasa: base-vN, CSV, tags y tarjeta «Subir v0.N». Si no:
  tarjeta bloqueada con los motivos.
- **Botón «Subir a Kaggle»** (`scripts/kaggle_submit.py`, CLI de KaggleFarm): un clic de Alba = un envío. Respeta el límite diario,
  espera la nota, la apunta en `eval/kaggle.json`, la tarjeta y el gráfico; si es peor que la mejor base activa, vuelve a esa base,
  marca la nueva como retirada (`"active": false` en `eval/results/base-vN.json`) y abre un diagnóstico para el analista.
- El consultor puede proponer un envío experimental de una variante rechazada por poco (como V-014) si la evidencia es ambigua.
- **MCP de Kaggle** (`.mcp.json`, https://www.kaggle.com/mcp, sin token; Alba inicia sesión con `authorize`): solo en sesiones
  interactivas del consultor, para leer notas y, con el OK explícito de Alba en cada envío, subir. El runner lo bloquea.
- A mano: `python scripts/make_submission.py --src models/base --name base-vX` → `dist/`; tag `vX.Y`; el mensaje lleva tag,
  backtest y holdout.

## Protocolo de permisos (detalle)
`board/permissions.py`, registro en `board/permissions.json`. Si a un agente le deniegan un comando, el runner lo clasifica:
*seguro* (solo lectura en el proyecto) → se concede solo y la tarjeta se reintenta; *prohibido* (publicar, borrar, instalar, red,
commits) → nunca, con el motivo anotado; *encadenado* (`&&`, `|`, heredoc, `VAR=x`) → se le explica cómo hacerlo; *a revisar* →
tarjeta «Solicitud de permiso» con botones Conceder / Denegar. A mano: `python board/permissions.py list|grant|deny`.

## Consumo de tokens (medido el 18-oct, ~17,7 M en el runner)
Evaluador 191 k por verificación (18 turnos), desarrollador 168 k, modelador 769 k y analista 544 k (opus). Medidas tomadas:
verificación mecánica previa (`scripts/verify_variant.py`, 0 tokens), evaluador en Haiku, topes de turnos por rol (`MAX_TURNS`
en board/runner.py) y este CLAUDE.md más corto. Volver a medir con `runs[].tokens` del panel tras unas cuantas tarjetas.

## Lecciones que justifican las reglas
- V-014: −0,0005 en local fue −0,0039 en Kaggle → no rechazar por «mejora menor que el ruido» si se repite con 2 semillas.
- V-019: mejoraba las prácticas y empeoraba el examen final (ponía a cero material escolar de temporada) → mirar siempre el holdout.
- v0.6 (V-018): copiaba al test el cierre de las tiendas 18 y 25 de agosto de 2016 → limpiar anomalías del año anterior.
- V-030: rechazada por tiempo y era mejor → el tiempo solo desempata.
- V-037: el holdout empeoraba (0,4051 → 0,4085) y Kaggle mejoró (0,38981 → 0,38839). El holdout acertó el sentido en 6 de 9
  versiones. Si una variante pasa las prácticas y la frena solo el holdout, se envía como experimento (OK de Alba, 18-oct) y se
  promueve con `promote.py V-xxx --lb <nota>` si Kaggle mejora. Repesca de V-022 por lo mismo: V-039 (T-103).
- V-038 (Huber): mismo caso, pero Kaggle empeoró (0,38839 → 0,39098) y el holdout acertó (0,4085 → 0,4134). Balance del holdout:
  7 de 10 aciertos. Sigue valiendo como alarma; el envío experimental es lo que decide.
- V-042 (linear_tree): mejoraba prácticas (−0,0016), holdout (0,4085 → 0,3996) y control, y en Kaggle fue 0,42499 (+0,037).
  Solo lo avisaba la comprobación de cambios en el test (material escolar +0,233 en log): las hojas lineales extrapolan la
  vuelta al cole. Esa alarma es la más fiable de todas: no se salta nunca sin un envío experimental.
