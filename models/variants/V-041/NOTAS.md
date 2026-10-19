# V-041 — perfil de paga por tienda
Nuevo rasgo `pay_prof`: para cada tienda, cuánto vende de más o de menos (en log, frente a su media de los 28 días anteriores) en cada tramo del mes (días 1-4, 12-15, 16-19, 27-31, resto), promediando sus últimos 365 días **anteriores al corte**. El modelo recibe el valor del tramo del día que predice.
Por qué: el modelo falla siempre igual alrededor de la paga; el día del mes crudo (V-016) se memorizó, un resumen por tienda no.
Se añade tanto al modelo directo como al recursivo. Nivel tienda (media de sus familias). Sin medir completo: lo hace el tester (quick f1 = 0.3889).
