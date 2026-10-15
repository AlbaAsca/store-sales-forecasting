# store-sales-forecasting — instrucciones para Claude Code

Proyecto de **aprendizaje** sobre la competición Getting Started de Kaggle
[Store Sales – Time Series Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting):
predecir 16 días de ventas de 54 tiendas × 33 familias de Corporación Favorita (Ecuador). Métrica: **RMSLE** (menor = mejor).
Objetivo: **aprender** forecasting con validación temporal y dejar un repo que se lea bien (README). No perseguir el leaderboard.

Trabajo individual sobre `main` (sin PRs). Python del proyecto: `.venv` (`python -m pip install -r requirements.txt`).
Panel: `run-panel.bat` → http://localhost:8021 · Autónomo: `run-agents.bat` (programado: `run-agents-scheduled.bat` cada 3 h)
Tests: `python -m pytest tests -q` · Datos: `data/` (fuera de git; ver README «Cómo reproducirlo»).

## Fechas
Sin plazo (Getting Started, leaderboard continuo). Alba tiene examen AWS el **30 nov 2026**: nada que la necesite entre el 26 y el 30.

## Método: cada cambio es un EXPERIMENTO
La sesión principal es el **consultor**: habla con Alba (español, directo, breve), prioriza y **mueve tarjetas**; no implementa
variantes. Delega en `.claude/agents/`:
- `investigador` (sonnet/low) busca técnicas en la discusión/notebooks de Kaggle, M5, blogs → hipótesis con ganancia esperada.
- `experto` (opus/high, **analista de errores**) mira dónde se equivoca el modelo (fold, tienda, familia, festivos).
- `desarrollador` (sonnet/medium) implementa una variante por tarea en `variants/V-xxx/`.
- `tester` (sonnet/low, **evaluador**) mide con el backtest y da veredicto. Quien implementa no evalúa.
- `arquitecto` (sonnet/medium) mantiene la estructura, trocea ideas grandes, vigila README y APRENDIZAJES.
- `modelador` (opus/high) lee **código** de soluciones de referencia y propone variantes en `docs/DISENO-MODELOS.md`.

Tarjeta: `V-xxx: <variante en una frase>` · `--desc`: hipótesis · cambio · **criterio fijado antes de medir**
(por defecto: RMSLE medio del backtest < base vigente y empeora como mucho 1 de los 4 folds; si empata, menos tiempo).
Resultado con `note`: RMSLE por fold, media, tiempo. Rechazada = `done` con «RECHAZADA». Aceptada = nueva base (tag `base-vX`).

## Variantes: una carpeta cada una (no negociable)
- `models/base/` es **la base vigente** (`model.py` con `fit_predict(history, future, ctx)`; contrato en su docstring).
  Nadie la toca salvo el consultor al promover una variante aceptada.
- Cada variante: `python scripts/new_variant.py V-xxx` → `variants/V-xxx/` = copia de la base + **solo su cambio** + `NOTAS.md`.
- Medir: `python scripts/backtest.py --src variants/V-xxx --name V-xxx` · Comparar: `python scripts/results.py compare base-vX V-xxx`.
- Aceptada → el consultor copia `variants/V-xxx/` a `models/base/`, tag `base-vX`, y las demás variantes se rehacen sobre la nueva base.

## Medición (no negociable)
1. **Validación temporal fija**: `eval/folds.json` (4 ventanas de 16 días antes del holdout). El modelo solo ve el pasado.
   **Holdout intocable**: `eval/holdout.json` (últimos 16 días), solo el consultor y solo antes de enviar.
2. **Comparación fold a fold y por familia** (`results.py compare`), no solo la media.
3. Si el modelo tiene aleatoriedad, repetir con otra semilla y anotar la variación antes de concluir.
4. Sin fugas: nada de ventas ni transacciones posteriores al corte. Si una variante mejora «demasiado», sospecha de fuga.
5. Iteración local en CPU (minutos). GPU de Kaggle (~19 h/mes, compartidas con otros proyectos) solo con coste en horas
   dicho a Alba antes y experimentos agrupados.

## Aprender (objetivo principal)
- Cada experimento cerrado deja 2-3 líneas en `docs/APRENDIZAJES.md`: qué se probó, qué pasó y por qué, en lenguaje llano.
- Concepto nuevo → se explica la primera vez (glosario al final de APRENDIZAJES.md).
- `README.md` es el escaparate: tabla de resultados al día y figuras en `docs/img/` (`python scripts/make_figures.py`).

## Panel (obligatorio)
`board/board.json` es la fuente de verdad. **Nunca lo edites a mano**: usa `board/board.py`.
- Crear: `python board/board.py add "Título" --owner <rol> --est <min> --prio alta|media|baja --desc "..."`
  (`--manual "qué debe hacer Alba"` si la necesita: descargar datos, subir a Kaggle, una decisión).
- Mover: `python board/board.py move T-012 doing|review|human|blocked|done --by <rol> --msg "..."` · `note` · `list`
- Todo trabajo tiene tarjeta y se actualiza al momento. Lo que espera medición va a **Bloqueado**, no a «Te necesita».

Estimaciones en **minutos de agente**. Calibración: investigación y variantes nuevas 2–3× lo estimado; herramientas y tests, lo previsto.

## Runner y permisos (Windows)
Permitido: python (del .venv), git status/diff/log, lectura, `python scripts/new_variant.py`, Kaggle CLI solo lectura.
Prohibido: cp/mv/rm, pip, comandos encadenados, git push, `kaggle competitions submit`/`download`, `kernels push`.
Todos los scripts que imprimen fuerzan UTF-8 (`sys.stdout.reconfigure(encoding="utf-8")`): la consola es cp1252.

## Envíos a Kaggle
`python scripts/make_submission.py --src models/base --name base-vX` → `dist/`. Tag `vX.Y` antes de subir; el mensaje incluye el tag
y el RMSLE de backtest y holdout. Subir es tarea `--manual` para Alba. Los agentes nunca envían.

## Commits
Autoría Alba Ascaso <albaasca@gmail.com>. En **inglés**, Conventional Commits, tarea al final: `feat(model): add weekday profile (T-012)`.
