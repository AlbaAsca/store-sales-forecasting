# 🛒 ¿Cuánto venderá mañana un supermercado?

**Previsión de ventas de 1.782 series temporales con validación temporal honesta**, contada paso a paso.
Lo hice para aprender *forecasting* después de Titanic y Kaggle Playground. Cada idea se trató como un experimento con
hipótesis, criterio fijado antes de medir y veredicto, y la mayor parte del trabajo lo hizo un equipo de agentes de IA
coordinado desde un tablero kanban (más abajo explico cómo).

> Competición: [Store Sales – Time Series Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting) (Kaggle, *Getting Started*)
> · Métrica: **RMSLE** (cuanto más bajo, mejor) · Todo corre en **CPU, en minutos**.

| | |
|---|---|
| 📈 **Mejor RMSLE en el backtest** | 0.4304 (base-v1 = V-001) · base-v0: 0.4745 |
| 🧪 **Experimentos cerrados** | 1 aceptado · 0 rechazados → [qué aprendí en cada uno](docs/APRENDIZAJES.md) |
| 🏁 **Leaderboard de Kaggle** | 0.45751 (v0.1, base-v0) · holdout 0.5191 |

---

## 1. El problema en 30 segundos

[Corporación Favorita](https://www.corporacionfavorita.com/) es una gran cadena de supermercados de Ecuador. Tenemos sus ventas
diarias de **2013 a agosto de 2017**: **54 tiendas × 33 familias de productos** (pan, bebidas, limpieza…), es decir,
**1.782 series temporales**. Hay que predecir los **16 días siguientes** de cada serie.

![Ventas totales por día](docs/img/ventas.png)

Las pistas que da Kaggle además de las ventas:

| Archivo | Qué es | ¿Lo sabemos en el futuro? |
|---|---|---|
| `train.csv` | ventas diarias y nº de productos en promoción | promociones **sí** (se planifican antes) |
| `stores.csv` | ciudad, tipo y *cluster* de cada tienda | sí (no cambia) |
| `oil.csv` | precio del petróleo (Ecuador depende mucho de él) | sí, Kaggle lo incluye |
| `holidays_events.csv` | festivos nacionales, regionales y locales, y días trasladados | sí |
| `transactions.csv` | nº de tickets por tienda y día | **no**: solo hasta hoy |

Esa última columna importa más de lo que parece (ver [fuga de información](#3-la-trampa-mirar-el-futuro-sin-querer)).

---

## 2. ¿Qué tiene de especial una serie temporal?

En Titanic las filas son **independientes**: un pasajero no depende del anterior, así que se pueden barajar y repartir al
azar entre entrenamiento y validación. Aquí **el orden importa**: lo que se vendió ayer dice mucho de lo que se venderá mañana.

Patrones que se ven a simple vista:

![Estacionalidad semanal y mensual](docs/img/semana.png)

- **Estacionalidad semanal:** el fin de semana se vende más.
- **Día de paga:** en Ecuador el sector público cobra el 15 y el último día del mes, y se nota.
- **Eventos:** el 1 de enero las tiendas cierran, diciembre se dispara y el **terremoto del 16 de abril de 2016** alteró las ventas durante semanas.
- **Muchos ceros:** algunas familias (libros, bebés…) apenas se venden en muchas tiendas.

![Familias: volumen y ceros](docs/img/familias.png)

---

## 3. La trampa: mirar el futuro sin querer

Si validas como en Titanic, con *k-fold* aleatorio, el modelo entrena con datos del jueves para «predecir» el miércoles
anterior. En la validación sale genial y en el test real se hunde. A eso se le llama **fuga de información** (*data leakage*):
el modelo usó información que no tendrá cuando prediga de verdad.

```mermaid
flowchart LR
    subgraph MAL["❌ K-fold aleatorio"]
        direction LR
        a1[lun] --- a2[mar] --- a3[mié ?] --- a4[jue] --- a5[vie ?]
    end
    subgraph BIEN["✅ Backtesting"]
        direction LR
        b1[lun] --- b2[mar] --- b3[mié] --> b4[jue ?] --- b5[vie ?]
    end
```

**La solución: backtesting** (validación temporal). Me sitúo en una fecha del pasado, entreno solo con lo anterior y predigo
los 16 días siguientes, igual que en el test de Kaggle. Lo repito en 4 fechas distintas (*folds*) para no fiarme de una sola
quincena:

![Backtest: 4 folds, holdout y test](docs/img/backtest.png)

- **4 folds** (azul): sirven para comparar ideas. Una idea se acepta si mejora la media **y** no empeora más de un fold.
- **Holdout** (rojo): los últimos 16 días. **No se toca** hasta el final; es el examen de verdad antes de enviar a Kaggle.
  Si mirase el holdout para decidir, acabaría ajustándome a él sin darme cuenta (otra forma de fuga, más sutil).
- El código que corta los datos ([`scripts/backtest.py`](scripts/backtest.py)) **solo le entrega al modelo el pasado**:
  la regla no depende de que me acuerde de cumplirla, está en el código. También corta `transactions` en la fecha del fold,
  porque en el test no existe.

---

## 4. La métrica: RMSLE

$$\text{RMSLE} = \sqrt{\frac{1}{n}\sum_i \big(\log(1+\hat y_i) - \log(1+y_i)\big)^2}$$

Al usar logaritmos mide **errores relativos**: predecir el doble cuesta lo mismo si vendes 10 panes que si vendes 10.000.
Así las 33 familias pesan parecido, aunque «GROCERY I» venda mil veces más que «BOOKS».

![RMSE frente a RMSLE](docs/img/rmsle.png)

Consecuencia práctica: muchos modelos se entrenan directamente sobre `log1p(ventas)` y al final se deshace con `expm1`.

---

## 5. Cómo trabajo: cada idea es un experimento

```mermaid
flowchart LR
    H["💡 Hipótesis<br/>«los festivos explican<br/>el error de diciembre»"] --> C["📏 Criterio fijado<br/>ANTES de medir"]
    C --> V["📁 Variante en su carpeta<br/>variants/V-xxx"]
    V --> M["🧪 Backtest<br/>4 folds, CPU"]
    M --> D{"¿Mejora la media<br/>sin romper folds?"}
    D -- sí --> B["✅ Nueva base<br/>tag base-vX"]
    D -- no --> R["❌ Rechazada<br/>(también se aprende)"]
    B --> A["📝 docs/APRENDIZAJES.md"]
    R --> A
    A --> H
```

- **La base no se toca nunca:** `models/base/` es el mejor modelo hasta hoy. Cada idea va en `variants/V-xxx/`,
  una copia con *un solo cambio*. Así, si mejora, sé exactamente por qué.
- **Comparo fold a fold y familia a familia**, no solo la media. Una mejora media puede esconder que algo se rompe en una
  familia concreta.
- **Las ideas rechazadas también cuentan:** quedan en [docs/APRENDIZAJES.md](docs/APRENDIZAJES.md), con el porqué.

### El equipo (agentes de IA con Claude Code)

```mermaid
flowchart TB
    Alba(("👩‍💻 Alba")) <--> Consultor["🧭 Consultor<br/>prioriza y mueve tarjetas"]
    Consultor --> Panel[("📋 Panel kanban<br/>board/board.json")]
    Panel --> Inv["🔎 Investigador<br/>Kaggle, M5, blogs"]
    Panel --> Mod["🧠 Modelador<br/>lee código de soluciones top"]
    Panel --> Exp["🩺 Analista de errores<br/>¿dónde falla el modelo?"]
    Panel --> Dev["🛠️ Desarrollador<br/>implementa la variante"]
    Panel --> Test["⚖️ Evaluador<br/>mide y da veredicto"]
    Panel --> Arq["🏗️ Arquitecto<br/>estructura y plan"]
    Inv & Mod & Exp -- "tarjetas V-xxx<br/>con hipótesis" --> Panel
    Dev -- "a revisión" --> Test
```

Quien implementa una variante nunca la evalúa. Un *runner* ([`board/runner.py`](board/runner.py)) recoge tarjetas del panel cada
3 horas y lanza al agente que toca, con permisos acotados: puede ejecutar Python y leer git, pero no instalar, borrar,
hacer push ni enviar nada a Kaggle. Los envíos los hago yo a mano.

---

## 6. Resultados

Backtest de 4 folds (RMSLE medio ± desviación; menor es mejor). La tabla se actualiza con cada experimento cerrado.

| Variante | Idea | RMSLE backtest | Folds que mejora | Veredicto |
|---|---|---|---|---|
| base-v0 | media de los últimos 14 días por tienda×familia | 0.4745 ± 0.0090 (f1 0.4738 · f2 0.4611 · f3 0.4769 · f4 0.4864) | — | línea base |
| V-001 | base-v0 × factor del día de la semana (8 sem.) por tienda×familia | 0.4304 ± 0.0106 (f1 0.4368 · f2 0.4143 · f3 0.4283 · f4 0.4423) | −0.044 | ✅ ACEPTADA |

![Progreso de los experimentos](docs/img/progreso.png)

---

## 7. Cómo reproducirlo

```bash
python -m venv .venv && .venv\Scripts\activate
python -m pip install -r requirements.txt
kaggle competitions download -c store-sales-time-series-forecasting -p data   # y descomprimir en data/
python scripts/backtest.py --src models/base --name base-v0                    # ~1 min en CPU
python scripts/results.py compare base-v0 V-001                                # variante contra base
python scripts/make_figures.py                                                 # regenera docs/img/
python scripts/make_submission.py --src models/base --name base-v0            # → dist/, para subir a Kaggle
python -m pytest tests -q
```

```
models/base/        el mejor modelo hasta hoy (model.py: fit_predict(history, future, ctx))
variants/V-xxx/     un experimento = una copia de la base + un cambio + NOTAS.md
eval/folds.json     los 4 folds del backtest (fijos)   · eval/holdout.json  el examen final (intocable)
eval/results/       resultados por experimento (RMSLE por fold y familia)
scripts/            backtest, comparación, figuras, envío
board/              panel kanban + runner de agentes   · .claude/agents/  definición de cada agente
docs/               APRENDIZAJES.md (bitácora), análisis de errores, diseño de modelos
```

---

## 8. Qué he aprendido

La bitácora completa está en [docs/APRENDIZAJES.md](docs/APRENDIZAJES.md), con un glosario de cada concepto nuevo.
Los tres aprendizajes más importantes se resumirán aquí al terminar el proyecto.
