# Aprendizajes

Bitácora de experimentos: 2-3 líneas por experimento cerrado (**qué se probó · qué pasó · por qué**), del más reciente al más antiguo.
Los conceptos nuevos se explican en el [glosario](#glosario) la primera vez que aparecen.

## Experimentos

### v0.8 · primera base preparada y subida sin intervención — 🏁 LB 0.39212 (mejor nota)
Qué: V-027 (promociones de los días de alrededor) la aceptó el evaluador, la promovió el script automático tras comprobar prácticas,
examen final (0.4139 → 0.4073), control y que ninguna tienda del test cambiara de golpe, y se subió con el botón del panel.
· Pasó: Kaggle 0.39720 → 0.39212 (−0.0051), la mayor mejora desde v0.4. · Por qué: la gente adelanta o retrasa compras alrededor de
una promoción, y esas promociones se conocen de antemano; además el examen final ya avisaba de una mejora grande.

### v0.7 · el año anterior, ahora limpio, sí funciona en Kaggle — 🏁 LB 0.39720 (mejor nota)
Qué: subir base-v7 (V-026: año anterior sin los cierres de 2016 + cero en series muertas salvo temporada). · Pasó: Kaggle 0.39940 → 0.39720
(−0.0022), la mejor nota hasta ahora; v0.6, con la misma idea sin limpiar, había dado 0.40871. · Por qué: la información del año anterior
era buena; lo que estropeaba v0.6 eran los cierres de las tiendas 18 y 25 que viajaban al test. Limpiar los datos antes de usarlos
convirtió un retroceso de +0.0093 en una mejora de −0.0022.

### V-027 · promociones de los días de alrededor — ✅ ACEPTADA (0.3838 / 0.3836 → 0.3829 / 0.3829)
Qué: además de saber si hay promoción el día que predice, el modelo ve la del día anterior, la del siguiente y cuántas promociones
habrá en las 16 días futuros (se conocen de antemano, no es trampa). · Pasó: mejora 4/4 prácticas, con las dos semillas, aunque poco
(−0.0009); beauty −0.007, pan y bollería +0.006; sin tiendas cerradas el control empeora algo (+0.0018). Tarda más (78 → 130 s).

### V-026 · año anterior sin cierres + cero en series muertas — ✅ ACEPTADA, nueva base-v7 (0.3852 → 0.3838 / 0.3836)
Qué: juntar V-025 (aprender del mismo periodo del año anterior quitando las tiendas cerradas entonces) y V-023 (predecir cero en las
series que llevan dos meses sin vender, salvo las de temporada). · Pasó: prácticas 0.3838/0.3836 con dos semillas (V-025 sola:
0.3841/0.3839), examen final 0.4179 → 0.4139, control sin cerradas 0.3927 → 0.3857. En el test, las tiendas 18 y 25 quedan como en
base-v5 (−0.0005 en log), al revés que en v0.6. · Por qué: cada idea corrige un error distinto y no se pisan. El material escolar que
la regla pone a cero es de tiendas de la Costa, donde el curso empieza en abril: en agosto no venden, tampoco en 2016.

### v0.6 · la vuelta al cole del año anterior empeora en Kaggle — 🏁 LB 0.40871 (se vuelve a base-v5)
Qué: subir base-v6 (V-018), que entrena también con el mismo periodo del año anterior. · Pasó: mejoraba en todo lo local (prácticas
0.3852 → 0.3839, examen final 0.4179 → 0.4148, control sin cerradas 0.3927 → 0.3865), pero Kaggle empeoró de 0.39940 a 0.40871.
· Por qué: del 16 al 31 de agosto de 2016 las tiendas 18 y 25 estuvieron cerradas (o casi); en 2017 venden con normalidad. El modelo
aprendió de ese año que «en estas fechas esas tiendas se hunden» y las predijo un 16 % más bajas justo en el test. Ninguna medida local
lo podía ver: el examen final es anterior a esas fechas y el control excluye las tiendas cerradas a propósito. Lección: si entrenas con
el año anterior, sus anomalías (cierres, terremotos, datos que faltan) viajan al futuro; hay que limpiarlas antes.

### v0.5 · envío experimental de una variante rechazada: Kaggle la premia — 🏁 LB 0.39940 (V-014 pasa a base-v5)
Qué: subir V-014 (LightGBM afinado), rechazada porque mejoraba solo 0.0005 en las prácticas, menos que el ruido de semilla. · Pasó: holdout
0.4187 → 0.4179 y Kaggle 0.40327 → 0.39940 (−0.0039, ocho veces más que en local). · Por qué: mejoraba en las 4 prácticas con dos semillas
distintas; que una mejora sea pequeña no quiere decir que sea azar si se repite siempre en la misma dirección. Lección: la regla «rechazar si
mejora menos que el ruido» era demasiado estricta; lo que hay que exigir es que la mejora se repita (varias semillas, casi todos los folds).

### v0.4 · cuarto envío: cuando las tres medidas locales coinciden, Kaggle también — 🏁 LB 0.40327
Qué: subir base-v4 (media del LightGBM directo y del recursivo). · Pasó: backtest 0.3904 → 0.3858, holdout 0.4378 → 0.4187, control
16-31 ago 2016 0.7696 → 0.7552, y Kaggle 0.41341 → 0.40327 (−0.010, el mayor salto desde v0.2). · Por qué: promediar dos modelos que se
equivocan de forma distinta reduce el error, y el pico de promos del 16-ago (diagnóstico T-027) le afecta menos. Lección: una mejora que se ve
en folds, holdout y control a la vez es mucho más fiable que una que solo se ve en la media de los folds (v0.3).

### v0.3 · tercer envío: el LightGBM mejora mucho en local y casi nada en Kaggle — 🏁 LB 0.41341
Qué: subir base-v3 (LightGBM global + promos + lag 364). · Pasó: backtest 0.4154 → 0.3904 (−0.025) y holdout 0.5244 → 0.4378 (−0.087),
pero Kaggle solo 0.41457 → 0.41341 (−0.001). · Por qué: aún no lo sabemos (tarjeta de diagnóstico). Lección provisional: la validación local
puede dejar de predecir el leaderboard cuando el modelo cambia de tipo; hay que entender la brecha antes de fiarse de la siguiente mejora.

### V-009 · estrategia recursiva y media directo+recursivo — ✅ ACEPTADA la media (0.3904 → 0.3860, semilla 1: 0.3856, mejora 4/4); ❌ RECHAZADO el recursivo solo (0.3894, ≈ variación)
Directo: un modelo predice los 16 días de golpe desde el corte. Recursivo: un modelo de 1 paso (lags cortos) predice mañana y se alimenta de su propia predicción 16 veces.
```
directo:    [historia]──────────────► d1 d2 … d16   (sin acumular error)
recursivo:  [historia]► d1 ► d2 ► … ► d16           (cada paso usa el anterior; el error se arrastra)
media:      exp(½·log directo + ½·log recursivo)
```
El recursivo solo apenas mejora (−0.001, lo que varía la semilla; peor en f1) porque acumula error; pero se equivoca de otra forma que el directo, y promediarlos en log baja la varianza: −0.0045 y 4/4 folds (coste: tiempo ×2.4). Ojo al promover: `MODE` por defecto en model.py es `rec`; hay que fijar `avg`.

### V-010 · ensemble de 3 semillas × 2 ventanas de entrenamiento — ❌ RECHAZADA (CV 0.3858 → 0.3856, semilla 7: 0.3854)
Se promediaron en log 6 modelos (semillas 0-2; historia completa y desde 2015). Mejora 4/4 folds pero solo −0.0002, menos que lo que ya varía entre semillas (~0.001), con el tiempo ×3 (97 → 312 s). Por qué: la base ya promedia directo+recursivo y 8 cortes, así que la varianza que quedaba por quitar era mínima; y con datos desde 2017 en los folds la ventana «desde 2015» apenas cambia nada. Más modelos del mismo tipo no sustituyen a información nueva.

### V-013 · mezcla en log de base-v3 (LightGBM) y base-v2 (estadístico) — ❌ RECHAZADA (CV 0.3893 con w=0.8 vs base-v4 0.3858)
Qué: pred = w·v3 + (1−w)·v2 en log1p, w ∈ {0.6…0.9}. · Pasó: curva suave con mínimo en w=0.8 (0.6→0.3912, 0.7→0.3899, 0.8→0.3893, 0.9→0.3895, 1.0→0.3904; semilla 1: 0.3891). Gana 0.0012 a v3 en 4/4 folds, pero pierde con base-v4 en 4/4 folds (+0.0035) y en el control de ago-2016 (+0.015, SCHOOL SUPPLIES +0.018). · Por qué: el estadístico aporta algo de varianza reducida, pero el promedio directo+recursivo de v4 ya capta casi todo eso con más calidad; v2 no sabe de promos ni de la vuelta al cole. El Carnaval (28-feb) no está en los folds, no se pudo medir.

### V-011 · acotar rasgos de promoción al p99 de entrenamiento — ❌ RECHAZADA (CV 0.3904 → 0.3908, semilla 1: 0.3910)
Qué: recortar promo_day y promo_ratio por familia al percentil 99 visto, para que el pico de promos del 16-ago (fuera de rango) no se extrapole. · Pasó: el CV queda igual (folds +0.0020/−0.0004/+0.0002/−0.0005), pero el 16-ago sigue
disparado frente al 17-ago: SCHOOL ×3.06 (antes ×3.29), LAWN ×2.77 (×3.91), LINGERIE ×1.84 (×2.32); el criterio pedía ≤ ×1.5. · Por qué: recortar ayuda algo, pero el salto lo siguen empujando otros rasgos (calendario, retardos); los árboles no extrapolan, así que el problema no era solo el valor extremo de la promo. Idea: atacar el pico por otro lado (p. ej. rasgo de día concreto o tope de predicción).

### V-012 · 24 cortes de entrenamiento + peso a lo reciente — ❌ RECHAZADA (CV 0.3904 → 0.3919, semilla 1: 0.3928)
Qué: pasar de 8 a 24 cortes semanales (más ejemplos por serie) y ponderar cada corte con vida media de 120 días. · Pasó: mejora f1/f2 y el control ago-2016 (0.7696 → 0.7596), pero empeora f3 (+0.006) y f4 (+0.005); media peor y ×4 de tiempo. · Por qué: los cortes extra solapan casi la misma información y el peso reciente no compensa; la ganancia en el control sugiere algo útil, pero no para los folds de junio-julio. No se probaron 16/40 cortes ni otras vidas medias.

### V-008 · 16 modelos directos (uno por horizonte) — ❌ RECHAZADA (RMSLE 0.3904 → 0.4833, empeora 4/4 folds)
Qué: estrategia multi-paso *directa*: en vez de un LightGBM con h como rasgo, 16 modelos, cada uno entrenado solo con su día de horizonte. · Pasó: 0.4793 / 0.4636 / 0.4835 / 0.5068 (semilla 7: 0.4817, variación 0.0016); peor sobre todo en LIQUOR/WINE/BEER, LAWN AND GARDEN, LADIESWEAR. · Por qué: cada modelo ve 1/16 de las filas (8 cortes × 1782 series) y sobreajusta; el modelo único comparte lo aprendido entre horizontes, y con pocos cortes eso pesa más que la especialización.

### V-007 · objetivo tweedie sobre ventas crudas — ❌ RECHAZADA (RMSLE 0.3904 → 0.4094, empeora 4/4 folds)
Qué: cambiar la función de pérdida del LightGBM de L2 sobre log1p(ventas) a tweedie (p=1.3) sobre ventas crudas. · Pasó: 0.4075 / 0.3885 / 0.4113 / 0.4304;
semilla 7 igual (0.4094): la variación es ~0.000, el empeoramiento (+0.019) es real. Peor en LAWN AND GARDEN +0.072, LADIESWEAR +0.046, SEAFOOD +0.043; 3× más lento. ·
Por qué: la función de pérdida es lo que el modelo intenta minimizar al entrenar; si no coincide con la métrica, optimiza otra cosa. RMSLE es L2 en log1p, así que L2 sobre log1p ya es exactamente la métrica. Tweedie pondera por escala (las series grandes mandan) y las familias de pocas ventas pierden.

### V-006 · estacionalidad anual (retardo 364) como rasgo — ✅ ACEPTADA (RMSLE 0.3946 → 0.3904, mejora 4/4 folds)
Qué: a V-005 se le añaden 3 rasgos: log1p de las ventas del mismo día un año antes (−364 d), su ventana ±3 d y la diferencia frente a la media 14 d previa a ese día. ·
Pasó: 0.3932 / 0.3796 / 0.3861 / 0.4029; otra semilla: 0.3903 (variación ~0.001). Mejoran GROCERY I −0.028, HOME CARE −0.022, DAIRY −0.021;
SCHOOL AND OFFICE queda casi igual (media 0.547 → 0.543: peor en f1/f2 ~+0.009, mejor en f3/f4). 24 s. · Por qué: las medias recientes no ven picos anuales;
mirar el mismo día del año anterior aporta esa memoria. Ganancia modesta y estable (≈10× la variación de semilla). El pico escolar sigue sin resolverse (solo hay 1 año previo útil).
(*Retardo (lag)*: valor de la serie de hace N días usado como rasgo.)

### V-005 · promociones como rasgos del LightGBM — ✅ ACEPTADA (RMSLE 0.4057 → 0.3946, mejora 4/4 folds)
Qué: V-004 + 3 rasgos (onpromotion del día objetivo, suma 14 d previos al corte, ratio día/media). · Pasó: 0.3949 / 0.3860 / 0.3918 / 0.4057;
otra semilla 0.3940 (variación ~0.001). Mejoran SCHOOL AND OFFICE −0.081, BEAUTY −0.056; ninguna familia empeora más de +0.005. Vs V-003: −0.063. ·
Por qué: el árbol aprende la respuesta a la promo por familia/tienda y no la mezcla con tendencia, que era el fallo de la beta fija de V-003.

### V-004 · LightGBM global con rasgos de la fecha de corte — ✅ ACEPTADA (RMSLE 0.4154 → 0.4057, mejora 3/4 folds)
Qué: un solo LightGBM para las 1782 series, entrenado con 8 cortes pasados (medias log 3/7/14/28/56 d, perfil semanal, h, dow, tienda y familia). ·
Pasó: 0.4041 / 0.3926 / 0.4007 / 0.4255 (f4 +0.003); otra semilla: 0.4046 (variación ~0.001). Empeoran SCHOOL AND OFFICE +0.042 y LIQUOR +0.023;
mejoran HARDWARE −0.033, AUTOMOTIVE −0.031. 15 s. · Por qué: un modelo global comparte información entre series (aprende cómo reacciona cada familia a su
nivel reciente) y una media por serie no lo ve. Aún sin promos, festivos ni anual: margen de mejora.
(*Modelo global*: un único modelo para muchas series, en vez de uno por serie.)

### v0.2 · segundo envío: ¿a quién creer, a los folds o al holdout? — 🏁 LB 0.41457
Qué: subir base-v2 (escala log), que mejoraba 4/4 folds (0.4304 → 0.4154) pero empeoraba el holdout (0.5109 → 0.5244). · Pasó: Kaggle
0.45751 → 0.41457, igual que decían los folds. · Por qué: el holdout es una sola quincena (1-15 ago) y mide sobre todo cómo le va al modelo
en esos días concretos; 4 folds promedian el ruido. Lección: una ventana de validación sola puede engañar; varias, mucho menos.

### V-003 · ajuste log por promociones (beta por familia) — ❌ RECHAZADA (RMSLE 0.4154 → 0.4571, empeora 4/4 folds)
Qué: sumar beta_familia·(log1p(promo día) − log1p(promo media 14 d)) a la predicción de V-002. · Pasó: 0.4311 / 0.4405 / 0.4625 / 0.4945;
mejoran BEAUTY −0.057 y SCHOOL −0.041, pero PRODUCE +0.394, DELI +0.241, POULTRY +0.229. Determinista (otra semilla idéntica). ·
Por qué: la beta por regresión mezcla promo con otros efectos (la promo suele coincidir con estacionalidad/tendencia) y en familias de frescos
saca ajustes grandes y erróneos. Si se reintenta: beta solo en familias donde sea significativa o dejar que lo aprenda el LightGBM (V-004).

### V-002 · media y perfil semanal en escala log — ✅ ACEPTADA (RMSLE 0.4304 → 0.4154, mejora 4/4 folds)
Qué: promediar log1p(ventas) en vez de ventas (14 d) y sumar el perfil del día de la semana también en log; luego expm1. · Pasó: mejora 4/4 folds (−0.009 a −0.020), sesgo log medio +0.015; sobre todo en LIQUOR/WINE/BEER (−0.050); empeora algo PRODUCE (+0.009).
Por qué: la métrica RMSLE es un error en log, así que promediar en log la alinea con ella y trata mejor los ceros e intermitentes. Modelo determinista: otra semilla da lo mismo. (Nota: se midió contra base-v1; el código parte de base-v0 y no usa el perfil multiplicativo de V-001.)

### V-001 · perfil por día de la semana — ✅ ACEPTADA (RMSLE 0.4745 → 0.4304, mejora 4/4 folds)
Qué: multiplicar la media de 14 días por un factor del día de la semana (media de ese día / media global, últimas 8 semanas, por tienda×familia). ·
Pasó: 0.4368 / 0.4143 / 0.4283 / 0.4423 (−0.044 de media); mejoran todas las familias grandes (LIQUOR/WINE/BEER −0.205, PRODUCE −0.153), empeoran
ligeramente BABY CARE +0.024 y HOME APPLIANCES +0.017. Modelo determinista: una semilla basta. · Por qué: la venta semanal tiene un ciclo fuerte
(fin de semana) que la media plana ignora; el error era sistemático, no ruido.

### v0.1 · primer envío a Kaggle (calibración) — 🏁 LB 0.45751
Qué: subir la base sin mejorar para comprobar si la validación local predice el leaderboard. · Pasó: backtest 0.4745, holdout 0.5191,
Kaggle 0.45751: el test se parece al backtest, no al holdout. · Por qué: los 16 días del holdout (1-15 ago, con la paga del 15) son
especialmente difíciles para una media plana; una sola ventana engaña, por eso usamos 4 folds. El backtest es fiable para decidir.

### base-v0 · media de los últimos 14 días — 📏 LÍNEA BASE (RMSLE 0.4745 ± 0.0090)
Qué: medir la predicción más simple (media de 14 días por tienda×familia) en los 4 folds. · Pasó: 0.4738 / 0.4611 / 0.4769 / 0.4864; muy estable entre folds
(el modelo no tiene aleatoriedad, así que una sola ejecución basta). · Por qué: no conoce el día de la semana ni festivos ni promociones; ese es el margen
que las variantes deben recortar. Cualquier variante debe bajar de 0.4745.

### T-032 · fold de control de vuelta al cole (c1) — herramienta, sin veredicto
Qué: añadido `control_folds` (c1 = 16-31 ago 2016, la misma estación que el test de Kaggle) que se mide y se muestra APARTE; no entra en la media ni en el veredicto. · Pasó: base-v3 saca 0.7696 en c1 frente a 0.3904 de media en los 4 folds de mayo-julio. · Por qué: el CV de mayo-julio no ve la vuelta al cole (material escolar en la Sierra), así que una mejora en CV puede no trasladarse al test. Además `backtest.py` avisa si hay hueco entre history y future (25-dic: no hay fila): un modelo con `start = history.max()+1` dejaría el último día sin predecir.

### V-017 · festivos por tienda (nacional, regional, local y evento) — ❌ RECHAZADA (0.3852 → 0.3849 / 0.3850 con semillas 42 y 7)
Qué: decirle al modelo, para cada tienda y día, si es festivo en su país, región o ciudad (respetando los festivos trasladados). · Pasó: −0.0003 de media con ambas semillas, pero empeora 2 de 4 folds (f1 +0.0004, f2 +0.0008); mejora f4 −0.0019 y c1 −0.002 (c1 sin tiendas cerradas: +0.002 peor con semilla 7). · Por qué: en las prácticas casi no hay festivos (~1 % de filas), así que el efecto es casi nulo y queda bajo el ruido; donde habría ganancia es el 10→11 de agosto, que no está en los folds de evaluación.

### V-014 · afinado de hiperparámetros del LightGBM — ❌ RECHAZADA (0.3858 → 0.3853/0.3851, mejora < 0.002)
Qué: probar 63 hojas, lr 0.03×700 rondas, min_data 100 (frente a los valores copiados de ceshine). · Pasó: mejora 4/4 folds con semillas 7 y 11, pero solo −0.0005/−0.0007 y el tiempo se triplica (97 s → ~300 s). · Por qué: los parámetros ya estaban cerca del óptimo; el modelo es poco sensible a ellos, y lo que queda de error está en las variables y la estructura, no en el afinado. Mejoras bajo 0.002 son indistinguibles del ruido de semilla.

### V-015 · rasgos de intermitencia (fracción de ceros 14/28/56 d, días desde la última venta) — ❌ RECHAZADA (0.3858 → 0.3854, semilla 1: 0.3855)
Qué: decirle al modelo cuánto «vende a golpes» cada serie. Una serie **intermitente** es la que tiene muchos días con venta 0 entre días con venta (p. ej. libros en una tienda pequeña). · Pasó: −0.0003 de media, 2 folds mejor y 2 peor, c1 mejora −0.0039; tiempo 97 s → 138 s. · Por qué: el modelo ya deducía la intermitencia de las medias y retardos (m56, lags); los rasgos nuevos repiten esa información y la mejora queda bajo el ruido de semilla (~0.001).

### V-016 · calendario de paga (día del mes, is_payday, días desde la paga, días a fin de mes) — ❌ RECHAZADA (0.3858 → 0.3878, semilla 1: 0.3874)
Qué: dar al modelo el día del mes y la distancia a la paga (15 y último día) para corregir el sesgo de principio/fin de mes. · Pasó: empeora 3/4 folds (+0.002 de media, ambas semillas), c1 +0.0022; LICOR/VINO/CERVEZA +0.020; tiempo ×1.9. · Por qué: con solo ~4 quincenas por fold, el día del mes es una variable que el árbol puede memorizar (sobreajuste) sin patrón estable; el efecto paga ya lo capturan los retardos y el perfil semanal.

### V-019 · predecir cero en series con ≥56 días seguidos sin vender — ✅ ACEPTADA (0.3852 → 0.3849 / 0.3850, mejora mínima)
Qué: regla dura tras el modelo: si una serie tienda×familia lleva 56 días a 0 justo antes del corte, se predice 0 en vez de «un poquito». · Pasó: −0.0003 (sem 42, 4/4 folds) y −0.0002 (sem 7, 3/4 folds); c1 −0.0003/−0.0015; BOOKS −0.005. Solo se midió N=56 (28 y 90 sin probar: el runner no deja fijar la variable ZERO_N). · Por qué: expm1 de una predicción pequeña no es cero y el RMSLE castiga ese error en series muertas; pocas series se ven afectadas, por eso la ganancia es pequeña pero consistente en dirección.
**Revisión del consultor: no se promueve.** En el examen final empeora (0.4179 → 0.4227): la regla da por muerto el material escolar de las tiendas 10, 13, 15 y 19, que no vende en todo el año y arranca con la vuelta al cole, justo las fechas del test de Kaggle. Lección: una regla dura (poner a 0) es peligrosa con productos de temporada; las prácticas de mayo-julio no lo podían ver. Se corrige en V-023.

### V-023 · regla de cero con excepción de temporada — ✅ ACEPTADA en prácticas (0.3852 → 0.3849 / 0.3850; examen final pendiente del consultor)
Qué: igual que V-019, pero no se pone a 0 una serie que vendió algo en las mismas fechas del año anterior (±1 semana). · Pasó: −0.0002 de media, 4/4 folds mejor con semilla 42 y 7 (0.3849/0.3850); c1 sin cerradas 0.3922/0.3914 (base 0.3927); tiempo 299 s → 106 s. · Por qué: la excepción protege el material escolar que despierta en agosto y mantiene el beneficio de la regla en las series realmente muertas. Falta confirmar en el holdout que ya no empeora.

### V-025 · año anterior sin copiar sus cierres — ✅ ACEPTADA (0.3852 → 0.3841 / 0.3839 con semillas 42 y 7)
Qué: V-018 (entrenar también con el mismo periodo del año anterior) pero quitando de esos ejemplos las tiendas cerradas (≥50 % de días a cero) y las series que se quedan a cero tras vender las 8 semanas previas. · Pasó: mejora 4/4 folds frente a base-v5; c1 sin cerradas 0.3863 (no empeora); en las predicciones del test, tiendas 18 y 25 frente a base-v5: +0.002 en log (V-018 daba −0.178), es decir, ya no salen hundidas. · Por qué: el filtro quita el accidente de agosto de 2016 y conserva la señal de temporada; las prácticas casi no cambian respecto a V-018 (0.3839) porque ese cierre no está en sus ventanas.

### V-018 · ejemplos de la vuelta al cole del año anterior en el entrenamiento — ✅ ACEPTADA (0.3852 → 0.3839 / 0.3840 con semillas 42 y 7)
Qué: añadir al entrenamiento del modelo directo 4 cortes de hace un año (mismo periodo, ±1 semana) para que vea cómo es un arranque de temporada. · Pasó: mejora 4/4 folds (f4 −0.0031), SCHOOL AND OFFICE −0.014, c1 0.7522 (sin cerradas 0.3865/0.3868), tiempo 90 s. · Por qué: ahora el modelo ve ejemplos reales de la subida estacional en vez de solo un rasgo «hace 364 días» que nunca había visto en acción; la ganancia en c1 es pequeña (−0.0005), así que conviene confirmarla en el holdout.

### V-020 · reparto distinto directo/recursivo por tipo de producto — ❌ RECHAZADA (0.3856 / 0.3857 vs 0.3852)
Qué: en vez de mezclar 50/50 «16 días de golpe» y «día a día», usar 65/35, 50/50 o 35/65 según lo a ratos que se vende el producto. · Pasó: empeora 3 de 4 prácticas (+0.0004 a +0.0007) con dos semillas; c1 0.7552 (base 0.7526). · Por qué: los dos métodos fallan de forma parecida en todos los grupos, así que el 50/50 ya estaba cerca del óptimo y los pesos a priori solo añaden ruido.

### V-030 · promediar 3 modelos con historiales de longitud distinta — ❌ RECHAZADA por tiempo (0.3822 / 0.3821 vs 0.3838)
Qué: tres copias del modelo, una mirando solo las últimas 1-2 semanas, otra ~2 meses y otra hasta un año, promediadas en log. · Pasó: mejora los 4 tramos con dos semillas (−0.0005 a −0.0030; c1 sin cerradas 0.3837 vs 0.3857), pero tarda 78 s → 308 s (×3.9) y el criterio pedía como mucho ×2. · Por qué: la variedad real de ventanas sí aporta algo (mejor que V-010, −0.0002), pero ~−0.0016 por cuadruplicar el coste es poco; queda como candidata si se abarata (p. ej. solo 2 ventanas o menos rondas).

### V-029 · un modelo por familia de producto — ❌ RECHAZADA (0.3870 / 0.3870 vs 0.3838)
Qué: entrenar 33 modelos (uno por familia, directo y recursivo) en vez de uno global, con árboles más pequeños. · Pasó: peor en los 4 tramos con dos semillas (+0.0003 a +0.0061); BREAD/BAKERY +0.046, BEAUTY +0.015; en la quincena de control sin cerradas mejora un pelo (0.3849 vs 0.3857); tiempo 78 s → 115 s. · Por qué: cada modelo ve ~33 veces menos ejemplos y pierde lo que las familias se enseñan entre sí (festivos, tendencias de tienda); el modelo global ya distingue la familia con su identificador.

### V-028 · nivel reciente de la tienda entera y de la familia en todo el país — ❌ RECHAZADA (0.3845 / 0.3848 vs 0.3838)
Qué: añadir a cada serie la media reciente (7 y 28 días) de su tienda completa y de su familia en las 54 tiendas, más la tendencia de la tienda. · Pasó: empeora 3 de 4 prácticas con dos semillas (f1 +0.002); LIQUOR +0.012/+0.016, BEVERAGES +0.005; c1 sin cerradas 0.3863/0.3853 (base 0.3857); tiempo 78 s → ~205 s. · Por qué: el modelo ya recibe tienda y familia como identificadores, así que el nivel agregado apenas aporta y añade ruido (y casi triplica el tiempo).

<!-- Formato:
### V-001 · perfil por día de la semana — ✅ ACEPTADA (RMSLE 0.52 → 0.47, mejora 4/4 folds)
Qué: … · Pasó: … · Por qué: …
-->

## Glosario

- **Serie temporal**: valores medidos en orden en el tiempo (ventas por día). El orden importa: no se pueden barajar las filas.
- **Horizonte**: cuántos pasos hacia delante predecimos. Aquí 16 días. Predecir el día 16 es más difícil que el día 1.
- **Backtesting (validación temporal)**: simular el pasado. Me coloco en una fecha, entreno solo con lo anterior y predigo lo siguiente.
- **Fold**: cada una de esas simulaciones. Usamos 4 para no fiarnos de una sola quincena.
- **Holdout**: un trozo de datos que se guarda sin mirar hasta el final, como examen; si lo usas para decidir, deja de ser examen.
- **Fuga de información (leakage)**: el modelo usa algo que no tendría al predecir de verdad (ventas futuras, transacciones del día).
  Síntoma típico: validación espectacular y test malo.
- **RMSLE**: error cuadrático medio sobre `log(1+y)`. Mide errores relativos (×2 cuesta igual en 10 que en 10.000 unidades).
- **Línea base (baseline)**: el modelo más simple razonable. Sirve de vara de medir: lo que no le gana, no aporta.
- **Estacionalidad**: patrón que se repite (semana, mes, año).
- **Función de pérdida**: la regla con la que el modelo puntúa sus errores mientras aprende (L2 = error² ; tweedie = pensada para datos con muchos ceros y colas largas). Conviene que case con la métrica final: L2 sobre log1p(ventas) es exactamente RMSLE, así que optimiza lo que se evalúa; tweedie sobre ventas crudas optimiza otra cosa (V-007 lo pone a prueba).

## V-035: el año anterior solo como forma, no como nivel — ❌ RECHAZADA (0.3820 vs 0.3814, semilla 42; 0.3819 vs 0.3815, semilla 7)
Se quitan las dos variables que dicen «cuánto se vendía hace un año» (el nivel) y se deja solo «cuánto subió o bajó» (la forma, ly_diff). GROCERY II mejora (−0.004), pero GROCERY I empeora (+0.011) y empeoran también PERSONAL CARE y PRODUCE; empeora 2 de 4 folds en ambas semillas y la quincena de control (0.3853 vs 0.3845) también. Por qué: el nivel del año pasado sí informa del tamaño de la familia en cada tienda; quitarlo corrige a una familia a costa de otras que se parecen. Tarda un 11 % más (429 → 478 s).

## V-034: reconciliación jerárquica (que tienda, familia y total cuadren) — ❌ RECHAZADA (0.3852 vs 0.3814, semilla 42; 0.3849 vs 0.3815, semilla 7)
Se predicen todos los niveles (total, tienda, familia, tienda×familia) y se ajustan a la vez por mínimos cuadrados ponderados para que sumen lo mismo. Empeora las 4 prácticas en las dos semillas (+0.004 de media) y tarda un 5 % más. Por qué: la suma ajustada arrastra el error de los niveles grandes hacia familias como lácteos o productos frescos (+0.02 a +0.04), y las familias pequeñas no ganan lo suficiente para compensarlo. Reconciliar ayuda cuando los niveles predicen peor por separado; aquí el modelo ya usa esa información.

## V-033: banda de incertidumbre (cuantiles 10/50/90) — ❌ RECHAZADA como base (la banda sí cubre)
Se añaden tres modelos que predicen el percentil 10, 50 y 90 de la venta, y con ellos una banda «entre X e Y». La previsión principal no cambia (RMSLE 0.3814, igual que base-v9). La banda acierta: cubre el 78-81 % de los días en los 4 folds y con dos semillas, dentro del objetivo 0.75-0.85. Pero la mediana sola empeora (0.391 de media frente a 0.383 de base-v8), así que no se promueve: sirve como información extra, no como envío. Tarda ×1.6 (429 → 688 s).

## V-032: una pizca de modelo tweedie en la media — ❌ RECHAZADA (0.3824 vs 0.3815, semilla 7)
Se mezcla un 20 % de un segundo modelo entrenado con otra pérdida (tweedie, sobre ventas sin comprimir) con la base. Empeora 3 de 4 prácticas (+0.0002, +0.0016, +0.0025) y tarda el doble (432 → 940 s). Por qué: tweedie solo ya era peor (0.4094) y sus errores no se compensan con los del modelo actual; no aporta diversidad útil, solo ruido.

## V-031: tres historiales juntos sobre la base nueva (aceptada)
Se promedian tres copias del modelo que miran 2 semanas, 2 meses y 1 año de historia, ahora sobre base-v8. Prácticas 0.3814/0.3815 frente a 0.3829: mejora en los 4 tramos y también sin tiendas cerradas. Las dos mejoras se suman porque cada ventana se equivoca en sitios distintos; tarda 7 min, pero el tiempo solo desempata.

## V-037: días de tienda cerrada como dato que falta (aceptada)
Un día en que la tienda entera vende 0 (cierre, 25-dic, días antes de abrir) se trataba como un cero más. Ahora esos días son «NaN» (dato ausente) en las medias y perfiles, y las medias ignoran los huecos. Con dos semillas baja un poco el error (0.3811 / 0.3813 frente a 0.3814 / 0.3815) y el control sin cerradas no cambia; la ganancia es pequeña, pero se repite. Por qué: el cero falso restaba nivel a las tiendas cerradas; quitarlo ayuda sin tocar el objetivo de entrenamiento.

## V-038: pérdida Huber, para que los picos raros pesen menos (aceptada)
La pérdida Huber penaliza igual que el error cuadrático los errores pequeños, pero solo linealmente los grandes (concepto: «función de pérdida» = lo que el modelo intenta minimizar). Así, los días con ventas disparatadas tiran menos del modelo. Con dos semillas baja el error (0.3806 / 0.3804 frente a 0.3811 / 0.3813), mejora 3/4 folds con semilla 42 y 4/4 con semilla 7, y el control sin cerradas baja de 0.3845 a 0.3838. Por qué: el error cuadrático obligaba al modelo a perseguir picos aislados; la ganancia es pequeña (≈ −0.0005/−0.0009) pero se repite.

## V-036: ventana ancha del año anterior (±14 días, no ±3) — ❌ RECHAZADA (0.3810 vs 0.3811, semilla 42; 0.3811 vs 0.3813, semilla 7)
Se añade el promedio de las ventas de hace un año en un mes alrededor de la misma fecha (`ly_win14`) y su subida frente a las 2 semanas previas (`ly_diff14`), para captar que la vuelta al cole llega antes cada año. Con semilla 42 mejora ligeramente (3/4 folds), pero con semilla 7 empeora 2 de 4 folds (f2 y f3 +0.0001) y la media apenas cambia (−0.0001 a −0.0002). Por qué: la idea era sana, pero el año anterior ya aparece con ±3 días y la ventana ancha solo repite la misma señal con más ruido; la diferencia está dentro del ruido entre semillas, así que no se promueve. Tarda 410 s, casi igual que la base.

## V-039: repesca de V-022 (series que se venden a ratos) sobre base-v10 (rechazada)
Añadimos al modelo la fracción de días con venta cero en las últimas 14/28/56 jornadas y los días desde la última venta, ignorando los días de cierre (así un cierre no cuenta como cero). Con dos semillas no mejora: 0.3815 frente a 0.3811 con semilla 42 y 0.3813 frente a 0.3813 con semilla 7; empeora 3 y 2 folds, y PRODUCE empeora mucho (+0.017 con semilla 42). Por qué: las series a ratos ya quedan bien recogidas por el promedio y el perfil semanal, y los nuevos rasgos añaden ruido en familias con muchas ventas nulas.

## V-040: corregir el sesgo por familia y día de la semana (rechazada)
Antes de predecir, el modelo vuelve a predecir la última ventana de 16 días del pasado (sin verla), mide su error medio en log por familia y día de la semana, lo encoge hacia 0 y lo suma a la predicción. Con dos semillas no mejora: 0.3816 frente a 0.3811 (semilla 42) y 0.3818 frente a 0.3813 (semilla 7); empeora 3 de 4 folds y tarda 4 veces más. Por qué: el error de una ventana reciente no es un sesgo estable; lo que parece sesgo (GROCERY II, licores) cambia de una ventana a otra y la corrección persigue ruido. Un sesgo de familia es más fácil de arreglar con el modelo mismo que con un parche posterior.

## V-041: perfil de paga por tienda y tramo del mes (rechazada)
Damos al modelo, por tienda, cuánto suele desviarse cada tramo del mes (1-4, 12-15, 16-19, 27-31, resto) respecto a su venta normal de los 28 días previos, usando solo los 365 días anteriores al corte. Con semilla 42 queda 0.3812 frente a 0.3811 y con semilla 7, 0.3813 frente a 0.3813; empeora 2 de 4 folds en ambas semillas (f1 y f4) y PRODUCE sube +0.022. Por qué: el sesgo de los días 1-4 y 27-31 es real, pero el promedio por tramo es tan grueso que mezcla meses buenos y malos y no corrige el error concreto; además el modelo ya recoge buena parte de ese patrón con el perfil semanal y las ventas recientes.
