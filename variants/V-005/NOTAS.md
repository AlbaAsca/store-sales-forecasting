# V-005 — promociones como rasgos del LightGBM global

Sobre V-004 (LightGBM global con medias log + perfil semanal). Añade 3 rasgos de `onpromotion`: el del día objetivo (se conoce de antemano),
la suma de los 14 días previos al corte y el ratio día/media de 14 d. Nada más.
Por qué: V-003 aplicaba una elasticidad fija por familia y falló; aquí el árbol aprende la respuesta a promos por familia y tienda.
Sin fuga: los cortes de entrenamiento usan la promo del día objetivo (dato planificado, existe también en `future`) y suma solo previa al corte.
Medición completa y veredicto: tester (comparar con base vigente y con V-003).
