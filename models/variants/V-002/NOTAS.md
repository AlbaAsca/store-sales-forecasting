# V-002: media y perfil semanal en escala log

La métrica (RMSLE) mide error en log, pero la base promediaba ventas en bruto: los días de pico inflaban la media y
sesgaba al alza (+0.10), sobre todo en series intermitentes con ceros.
Cambio: se promedia log1p de las ventas (14 d) y se suma el perfil del día de la semana también en log (8 semanas,
por tienda×familia); se deshace con expm1 y se recorta a 0.
Construida sobre base-v0 (V-001 aún no es base); sustituye por completo el perfil multiplicativo de V-001.
