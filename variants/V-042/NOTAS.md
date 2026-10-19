# V-042 — hojas lineales (linear_tree)
Un árbol solo predice valores ya vistos, así que se queda corto cuando una familia vende más que nunca (p. ej. GROCERY II).
Cambio único: `linear_tree=True` en los LightGBM del directo y del recursivo (comparten `PARAMS`), con `linear_lambda`
(env `V042_LAMBDA`, defecto 1.0). Cada hoja ajusta una recta y puede seguir una subida.
Coste esperado ×2-3; sin otros cambios sobre base-v10.
