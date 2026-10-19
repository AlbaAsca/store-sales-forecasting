# V-023: regla de «cero» sin tocar productos de temporada
Sobre base-v5: como V-019, si una serie lleva ZERO_N (56) días seguidos a 0 antes del corte se predice 0.
Novedad: no se aplica si la serie vendió algo en el mismo tramo del año anterior (±1 semana), p. ej. material escolar que arranca con la vuelta al cole.
Solo usa datos anteriores al corte (sin fugas). Si no hay un año de historia, la excepción no se aplica.
