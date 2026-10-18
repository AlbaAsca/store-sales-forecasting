# Notas del investigador

## 2026-10-17 · T-043 búsqueda web: variables y técnicas de las mejores soluciones
Limitaciones: el Kaggle CLI (`kernels list/pull`) fue **denegado** en la sesión (sin aprobación) y Kaggle no se puede leer con WebFetch,
así que **no se pudo ordenar los notebooks por votos ni leer los top**. Lo siguiente sale de repos de GitHub/Medium/foros con la misma
competición o su antecesora (Favorita 2018). Ninguno es «top del leaderboard» verificado. Pendiente (humano): `kaggle kernels list ... --sort-by voteCount`.

### 1. Qué variables usan y qué consiguen (Store Sales 2022+)
| Fuente | Resultado | Hallazgos útiles |
|---|---|---|
| [gersonlramos](https://github.com/gersonlramos/Store-Sales---Time-Series-Forecasting) (LightGBM directo+recursivo) | LB público 0.38924 | Lo más documentado, con rechazos. Ver abajo |
| [beratmertkayacan](https://github.com/beratmertkayacan/kaggle-store-sales) (LightGBM log1p, 31 rasgos) | val 0.3691 (1 ventana, 15 d; transacciones reales = fuga) | Con transacciones rellenadas con media tienda×día: 0.3751; con 0: 2.76 → las transacciones del futuro no existen, no usar |
| [fredp-gb](https://github.com/fredp-gb/favorita-store-sales) (LightGBM+TFT) | holdout 0.3886, LB 0.412 | Terremoto como ventana puntual, petróleo efecto pequeño (resumen de búsqueda, no leído a fondo) |
| [Michael_Ram, Medium](https://medium.com/@Michael_Ram/my-first-foray-into-kaggles-store-sales-forecasting-25e2d2edf366) | — (403 al leerlo) | Petróleo rodante 7/14/28, traslados/puentes, días desde terremoto; lags y medias móviles dominan la importancia (según resumen de búsqueda; **no verificado**) |

Lo que gersonlramos midió (LB público):
- **Aportó:** modelos por horizonte −0.0096 (en nosotros V-008 empeoró, mucho: no trasladable tal cual); **regla de «serie dormida → 0 duro» −0.0153** (la mayor ganancia
  individual tras el baseline); mezcla recursivo/directo por familia 70/30 −0.0051; peso de mezcla **según familia** (solo 3 familias) −0.0015; promociones como intensidad relativa por familia/tienda y con futuras conocidas (−0.04, la mayor de todas, pero partía de un baseline flojo 0.55).
- **Rechazó:** transacciones (+0.003), petróleo (+0.0008; r≈−0.02 sin tendencia), festivo binario (×1.01), festivos regionales (≤5 observaciones por serie), flag de terremoto (peor de 3 tratamientos; mejor «reparar» el panel), vuelta al cole por región (perdió en 3 ventanas), lag_364 (rechazado también en V-006/ nuestra base), tweedie/Poisson (perdió), XGBoost (correlación de residuos 0.97–0.99), corrección de sesgo, dos etapas P(venta)×magnitud (empate).
- Coincide con nuestro historial: tweedie ❌ (V-007), 16 modelos ❌ (V-008), intermitencia como rasgos ❌ (V-015), mezcla con estadístico ❌ (V-013).

### 2. Favorita 2018 y M5 aplicables
- Favorita 5.º ([fast.ai foro](https://forums.fast.ai/t/5th-place-solution-of-favorita-grocery-sales-forecasting/10009)): LightGBM con medias/promos/**conteo de ceros** en ventanas deslizantes, partidas por promo/día de semana; 16 modelos; validación empezando en el mismo día de la semana que el test; **varios cortes aleatorios de entrenamiento** (ya lo hace V-012); promedio de semillas. El ganador mezcló GBM y redes ([arXiv 2009.07701](https://arxiv.org/pdf/2009.07701)).
- M5 1.º (resumen [KAIST](https://dspace.kaist.ac.kr/handle/10203/299580)): media simple de modelos LightGBM directos y recursivos entrenados a varios niveles (pooling parcial). Ya tenemos directo+recursivo (base-v4); el pooling por niveles (modelo por tienda / por familia) **no está probado** y gersonlramos vio que modelos por familia ayudaron al recursivo pero no al directo. No verificado que el 1.º usara tweedie (en nosotros ❌).

### 3. Qué no tenemos aún (descontando T-041/T-042 y backlog T-045/46/47)
Ya en backlog: paga/día del mes (T-045), festivo por tienda (T-046), cortes del año anterior (T-047). Evidencia web **débil** para festivos y paga (nadie midió ganancia clara; paga solo aparece en proyectos de estudiante). No añado tarjeta.
Nuevo y con evidencia: (a) **regla de series dormidas → 0** (post-proceso, ≈0 CPU); (b) **peso directo/recursivo por familia** en vez de 50/50.

### Comparación
| Técnica | Ganancia esperada | CPU | Dificultad | Aprendizaje |
|---|---|---|---|---|
| Dormida→0 | media (0.003–0.015; el 22 % del error está en ceros) | ≈0 | baja | intermitencia sin rasgos de modelo |
| Peso por familia directo/recursivo | baja (0.001–0.002), riesgo de sobreajustar 4 folds | ≈0 si se guardan ambas predicciones | media | mezcla por segmento |
| Transacciones / petróleo | ≈0 o negativa | bajo | media | no existen en el futuro |
| Terremoto flag | negativa | — | baja | tratar contaminación en el panel |
| Festivos binarios / regionales | ≈0 (×1.01) | bajo | media | ya en T-046 |

### Tarjetas creadas
- V-019 serie dormida → 0 (alta). V-020 peso directo/recursivo por familia (media). Ver panel.

## 2026-10-18 · T-069 notebooks públicos leídos de verdad (código en `data/kaggle-code/`, fuera de git)
`kernels list --sort-by voteCount`: el top 6 por votos son los ejercicios/tutorial de Ryan Holbrook (23k–66k votos; regresión lineal con
tendencia + Fourier + híbrido lineal+XGBoost). Son didácticos, no competitivos: no se leen más (ya cubierto: V-001/V-002 y el híbrido ≈ LightGBM sobre log).
Leídos (código o markdown con resultados): los 3 competitivos de verdad. Scripts auxiliares: `scripts/analysis/ipynb_code.py`, `ipynb_grep.py`.
Solo se descargaron 5 (los 3 de abajo + el ejercicio híbrido y el curso de Ivan Lydkin, estos dos sin leer a fondo); no hay 5–8 competitivos con código útil.

| Notebook (votos) | Qué hace | Nota | Qué nos falta |
|---|---|---|---|
| [ferdinandberr · Darts global models](https://www.kaggle.com/code/ferdinandberr/darts-forecasting-deep-learning-global-models) (691) | Suavizado exponencial local por serie (base); **33 LightGBM globales, uno por familia**, log1p+escalado, covariables estáticas; también N-HiTS/LSTM/TFT (GPU, Optuna); **ceros forzados** si la serie está a 0 | Suavizado exp. 0.40578 LB; LightGBM por familia **0.38558 LB (n.º 1 en sept-2022)**; val 16 d: suavizado 0.37411 | **Un modelo por familia** (no probado nunca como LightGBM directo; V-008 fue por horizonte, otra cosa). Entrenar solo con las últimas N muestras por serie según modelo |
| [chongzhenjie · Global LightGBM](https://www.kaggle.com/code/chongzhenjie/ecuador-store-sales-global-forecasting-lightgbm) (426) | Reimplementa lo anterior: CV con origen móvil, ensemble de LightGBM con lags distintos (7, 63, 365, 730), medias móviles 7/28 de petróleo y promoción como covariables, cero si 21 días a cero, festivos agrupados por nombre y sin los trasladados, relleno del 25-dic y transacciones | Promedio de dos ensembles (todo vs desde 2015) mejor que cada uno; cifra exacta no visible en el código | **Ensemble con historiales de distinta longitud** (V-010 repetía el mismo tipo → −0.0002); medias móviles de promoción pasadas (V-027 cubre las vecinas) |
| [ekrembayar · Comprehensive Guide](https://www.kaggle.com/code/ekrembayar/store-sales-ts-forecasting-a-comprehensive-guide) (2943) | Solo EDA: transacciones (correlación alta con ventas), petróleo interpolado, festivos | Sin modelo ni nota | Nada accionable: transacciones no existen en el futuro; petróleo ya rechazado (gersonlramos) |

Ya cubierto por nosotros: ceros (V-019/V-023/V-024), festivos por tienda (V-017), promos vecinas (V-027), estado de tienda/familia (V-028),
directo+recursivo (base-v4), cortes múltiples (V-012).
Observación: nuestro LB 0.3972 es peor que el 0.38558 de 2022 (ese LB era de otra fecha y otro reparto público/privado: no comparable al 100 %), así que puede haber margen.

### Comparación
| Técnica | Ganancia esperada | CPU | Dificultad | Aprendizaje |
|---|---|---|---|---|
| Un LightGBM por familia (33) | media-baja (0.002–0.008; gersonlramos vio que ayudó solo al recursivo) | ×1–2 | baja-media | pooling total vs parcial |
| Ensemble con ventanas de historial muy distintas | baja (0.001–0.003) | ×2 | baja | diversidad real vs semillas |
| Redes (N-HiTS/TFT) | desconocida | GPU | alta | fuera de alcance CPU |

### Tarjetas creadas
- V-029 (un modelo por familia) y V-030 (ensemble con ventanas de historial distintas). Ver panel.

## 2026-10-18 · T-082 spec-kit (GitHub) para la plantilla agent-board

**Qué es.** Flujo «desarrollo guiado por especificaciones»: Constitución → Specify → Plan → Tasks → Implement → Converge. Se instala con `uv tool install specify-cli` y `specify init <proyecto> --integration <agente>`; los comandos son «skills» del agente (`/speckit-specify`… en la doc actual; `/speckit.specify`… en la doc de método). Número de versión: no verificable desde las páginas leídas (docs actualizadas 2026-09-28).

**Ficheros** (según spec-driven.md): `memory/constitution.md` (único, 9 artículos con «gates») y, por funcionalidad, `specs/NNN-nombre/` con `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`. Además checklists de calidad y marcadores `[NEEDS CLARIFICATION]`.

**Contexto añadido por tarea (estimación, no medido: no se instaló nada).** 7+ documentos de ~3–8 KB ya rellenos → **≈ 20–40 KB por funcionalidad** (+ constitución 5–10 KB releída siempre), frente a **≈ 1–2 KB** de una tarjeta nuestra (título + descripción llana + `## Técnico`). Es ×15–30 de contexto. Un agente que implementa lee como mínimo spec + plan + tasks.

### Comparación
| Criterio | Tarjeta actual (board + agentes) | spec-kit |
|---|---|---|
| Contexto por tarea | ≈1–2 KB | ≈20–40 KB (est.) |
| Define «hecho» | «Cómo sabremos…» + criterio exacto | Criterios de aceptación en spec + checklist |
| Reglas permanentes | CLAUDE.md + agentes | constitution.md (equivalente) |
| Requisitos que cambian | Se reescribe la tarjeta | Bueno: spec versionada, clarificaciones, converge |
| Trazabilidad requisito→tarea→código | Débil | Fuerte |
| Coste de ceremonia | Mínimo | Alto; mal para tareas de 30 min |
| Encaja en forecasting/experimentos | Sí | No (el criterio es una métrica, no una historia de usuario) |

### Recomendación: usar SOLO UNA PARTE en agent-board, y solo en proyectos de producto
- **No** adoptarlo entero: duplica lo que ya cubren tarjeta + CLAUDE.md + agentes y multiplica el contexto.
- **Sí** copiar dos ideas baratas como plantilla opcional (`docs/spec-plantilla.md`, ≤3 KB): (1) una *spec* corta por funcionalidad con historias, criterios de aceptación y marcadores `[NEEDS CLARIFICATION]`; (2) un paso de *clarificar* antes de crear tarjetas. La tarjeta enlaza la spec en vez de duplicarla; la «constitución» ya es CLAUDE.md.
- Reconsiderar el flujo completo solo si un proyecto de producto tiene >5 funcionalidades con requisitos cambiantes y varios agentes escribiendo código.
- Límite: tamaños estimados; medirlos exige instalar `specify-cli` (no permitido en modo autónomo).

Fuentes: github.com/github/spec-kit · github.github.io/spec-kit/ · raw.githubusercontent.com/github/spec-kit/main/spec-driven.md

### Tarjetas creadas
- T-088 (plantilla de especificación corta para agent-board, prio baja). Ver panel.
