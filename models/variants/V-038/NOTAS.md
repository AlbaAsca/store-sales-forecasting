# V-038 — pérdida Huber
Cambio único: el modelo aprende con pérdida Huber (alpha=1.0, sobre log1p) en vez de error cuadrático.
Los errores pequeños se penalizan igual, pero los grandes (días con picos disparatados) pesan solo linealmente,
así esos días confunden menos. Sigue en escala log (a diferencia de tweedie). Mismo PARAMS para directo y recursivo.
Alternativa si no cambia nada: `--env HUBER_ALPHA=0.7`.
