# store-sales-forecasting — instrucciones para Claude Code

Proyecto de **aprendizaje** sobre Kaggle [Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting):
predecir 16 días de ventas de 54 tiendas × 33 familias (Favorita, Ecuador). Métrica **RMSLE** (menor = mejor). Objetivo: aprender y
dejar un repo que se lea bien. Trabajo sobre `main`. Python: `.venv`. Tests: `python -m pytest tests -q`. Datos en `data/` (fuera de git).
La sesión principal (consultor) lee además `docs/CONSULTOR.md`.

## Agentes (.claude/agents/)
investigador (busca técnicas) · experto (analista de errores) · desarrollador (implementa variantes) · tester (evaluador: verifica;
quien implementa no evalúa) · arquitecto (estructura y documentación) · modelador (lee código de soluciones de referencia).

## Tarjetas
`board/board.json` solo con `board/board.py` (`add`, `move`, `note`, `desc`, `list`). Comandos de board.py en una sola línea, sin
encadenar; en `--desc` los saltos de línea se escriben `\n`. Descripción para una persona: arriba 2-4 frases llanas (problema,
idea, por qué) y «Cómo sabremos si funciona: …»; lo técnico debajo de `## Técnico`. «Te necesita» solo para lo que únicamente
puede hacer Alba; lo que espera otra cosa va a «Bloqueado». Estimaciones en minutos de agente.

## Experimentos (no negociable)
- `models/base/` es la base vigente; nadie la toca salvo la promoción. Cada variante: `python scripts/new_variant.py V-xxx` →
  `variants/V-xxx/` = copia de la base + **un solo cambio** + `NOTAS.md`.
- Criterio por defecto, fijado antes de medir: RMSLE medio < base **con 2 semillas** (42 y 7) y como mucho 1 de 4 folds peor. Una
  mejora pequeña que se repite cuenta; el tiempo solo desempata (salvo > 15 min por medición).
- Medir: `python scripts/verify_variant.py V-xxx` (backtest con las dos semillas, comparación y veredicto) o, a mano,
  `python scripts/backtest.py --src variants/V-xxx --name V-xxx [--seed 7] [--env VAR=valor]` y `python scripts/results.py compare`.
- Validación: 4 folds fijos (`eval/folds.json`) + control de agosto 2016 (mirar «sin cerradas»). El holdout (`eval/holdout.json`)
  no se usa para decidir. Sin fugas: nada posterior al corte; si mejora «demasiado», sospecha.
- Cada experimento cerrado: 2-3 líneas llanas en `docs/APRENDIZAJES.md` (concepto nuevo → al glosario) y su fila en el README.

## Runner y permisos
Permitido: python del .venv, git status/diff/log/show, lectura, Edit/Write. Prohibido: cp/mv/rm, pip, red, git add/commit/push,
comandos encadenados, `VAR=x python …`, `python -c` de varias líneas, heredoc, cualquier subida a Kaggle. Si necesitas un permiso,
escribe `PERMISO: <comando> — <para qué>` antes de RESULT. Los scripts que imprimen fuerzan UTF-8 (consola cp1252).

## Commits
Los hace el runner. A mano: autoría Alba Ascaso <albaasca@gmail.com>, **sin líneas de coautoría**, inglés, Conventional Commits,
tarea al final: `feat(model): add weekday profile (T-012)`.
