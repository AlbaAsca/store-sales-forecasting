# Notas del modelador

## 2026-10-17 · ronda T-065 · tarjetas pendientes de crear (el runner bloqueó `board.py add` con «## Técnico» multilínea)

Detalle técnico y fuentes en `docs/DISENO-MODELOS.md`, sección «ronda T-065».

### V-027: avisar al modelo de las promociones de los días de alrededor, no solo del día que predice
owner desarrollador · est 25 · prio media

Hoy el modelo solo sabe si el producto está en promoción el mismo día que predice y cuántas promociones hubo en las dos semanas anteriores. Pero una promoción mueve las compras de los días cercanos: la gente espera a que empiece o compra de más justo antes de que acabe. Las promociones de las dos semanas siguientes ya se conocen de antemano, así que se le pueden dar al modelo sin hacer trampa.
Cómo sabremos si funciona: el error medio de las prácticas baja frente a la base actual con dos semillas y no empeora más de una de las cuatro ventanas.

## Técnico
Fuente: ceshine/lgbm-starter (`promo_i` de los 16 días futuros), Favorita 1.º (suma de promos de los 16 días siguientes).
Cambio en `_features` y `_step_feats`: `promo_fut16 = P[:, origin:origin+16].sum(1)`; `promo_prev_day = P[:, origin+j-1]`; `promo_next_day = P[:, origin+j+1]` (j=15 → NaN siempre).
Criterio: CV medio < base-v7 (0.3838/0.3836) con semillas 42 y 7, empeora ≤ 1 de 4 folds; anotar c1 sin las tiendas 18/25 y el tiempo.

### V-028: enseñar al modelo cómo va la tienda entera y la familia en todas las tiendas
owner desarrollador · est 30 · prio media

Ahora cada serie (una familia en una tienda) solo se mira a sí misma. Si una tienda entera vende menos esta semana, o una familia sube en todo el país, el modelo no lo ve salvo por la propia serie, que en productos pequeños es muy ruidosa. Los ganadores de la competición de Favorita añadían el nivel reciente de la tienda completa y el de la familia sumando todas las tiendas.
Cómo sabremos si funciona: el error medio de las prácticas baja frente a la base actual con dos semillas y no empeora más de una de las cuatro ventanas.

## Técnico
Fuente: Favorita 1.º/2.º (rasgos agregados a nivel de tienda y de artículo), M5 1.º (modelos por tienda/categoría).
Cambio en `_features` y `_step_feats`: `st_m7`, `st_m28` = media log1p de las 33 familias de la tienda en [origin−w, origin); `fam_m7`, `fam_m28` = media log1p de la familia en las 54 tiendas; `st_trend = st_m7 − st_m28`. Solo fechas < corte.
Criterio: el mismo que V-027.
