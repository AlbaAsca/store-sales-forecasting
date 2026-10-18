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

Cómo escribir la descripción de una tarjeta (la lee Alba, una persona que está aprendiendo, no un robot):
arriba, 2-4 frases en lenguaje llano: qué problema hay, qué idea probamos y por qué; después una línea
«Cómo sabremos si funciona: …» en palabras. Los datos técnicos (fuentes, nombres de variables, fórmulas, números,
criterio exacto) van al final, debajo de una línea que diga exactamente «## Técnico». Sin siglas ni nombres de código en la parte de arriba.
Título en lenguaje llano. Tarjeta: `V-xxx: <variante en una frase>` · `--desc`: hipótesis · cambio · **criterio fijado antes de medir**
(por defecto: RMSLE medio del backtest < base vigente **con al menos 2 semillas** y empeora como mucho 1 de los 4 folds; si empata, menos tiempo).
El tiempo solo desempata: no se rechaza una mejora por tardar más, salvo que una medición completa pase de 15 min (lección de V-030).
No rechazar solo porque la mejora sea menor que la variación de semilla: si se repite en la misma dirección con 2 semillas, se acepta
(lección de V-014: −0.0005 en local fue −0.0039 en Kaggle).
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
**Botón «Subir a Kaggle»** (18-oct): la tarjeta de subida que crea la promoción automática lleva los datos del envío; Alba pulsa el
botón en el panel y `scripts/kaggle_submit.py` (CLI de Kaggle de KaggleFarm) sube el CSV, respeta el límite diario, espera la nota,
la apunta en eval/kaggle.json, la tarjeta y el gráfico, y si es peor que la mejor base activa vuelve a esa base, marca la nueva como
retirada y abre una tarjeta de diagnóstico para el analista. Un clic de Alba = un envío; los agentes siguen sin poder subir.
**Automático** (petición de Alba, 18-oct): cuando el tester acepta una variante crea la tarjeta «Promover V-xxx…» para el
consultor, y el runner ejecuta `scripts/promote.py V-xxx` sin agente: prácticas con todas las semillas, examen final, control sin
cerradas y que ninguna tienda o familia del test cambie de golpe frente a la base. Si pasa, promueve a base-vN, genera el CSV, pone
los tags y deja la tarjeta «Subir v0.N» para Alba; si no, la tarjeta queda bloqueada con los motivos. Una base retirada tras Kaggle
se marca `"active": false` en eval/results/base-vN.json.
**Quién lo decide: el consultor, por iniciativa propia** (petición de Alba, 17-oct). En cuanto haya una variante aceptada, el consultor
sin esperar a que se lo pidan: la promueve a base, mide holdout y control sin tiendas cerradas, genera el CSV, pone los tags y crea la
tarjeta `--manual` de subida con el mensaje exacto. También puede proponer un envío experimental de una variante rechazada por poco
(como V-014) si la evidencia local es ambigua. Al empezar cada conversación, el consultor revisa el panel por si hay algo que promover.
**MCP de Kaggle** (`.mcp.json`, servidor remoto https://www.kaggle.com/mcp, sin token: Alba inicia sesión con la herramienta `authorize`).
Solo lo usa el consultor en sesiones interactivas: para leer puntuaciones y, **con el OK explícito de Alba en cada envío**, subir el CSV.
El runner lo bloquea (`--strict-mcp-config` y `mcp__kaggle` en DENIED): los agentes autónomos nunca lo ven.

## Commits
Autoría Alba Ascaso <albaasca@gmail.com>. En **inglés**, Conventional Commits, tarea al final: `feat(model): add weekday profile (T-012)`.
