# Plantilla de tarjeta «especificación» (agent-board, AB-01)

Opcional, solo para proyectos de **producto** con requisitos cambiantes. En forecasting no se usa (el criterio es una métrica).

## Decisiones
- **La spec vive dentro de la tarjeta** (`--desc`), bajo `## Especificación`. Cero ficheros nuevos por tarea.
- De spec-kit se toma: spec simplificada, marca `[NEEDS CLARIFICATION]`, constitución de ≤1 página.
- Descartado: `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`. Motivo: ×15–30 de contexto (NOTAS-investigador, T-082); las tareas ya son tarjetas del tablero y el plan lo cubre el diseño en `docs/`.
- Constitución = una sección del CLAUDE.md del proyecto (no un fichero aparte), ≤1 página, releída siempre.
- Una tarjeta con `[NEEDS CLARIFICATION]` no se implementa: el arquitecto o Alba lo resuelven primero (`--manual` si es de Alba).
- Presupuesto: la plantilla rellena ≤2 KB por tarjeta.

## Plantilla (copiar en `--desc`, `\n` por salto de línea)

```
<2-4 frases llanas: problema, idea, por qué>
Cómo sabremos si funciona: <en palabras>
## Especificación
Historias:
- Como <quién>, quiero <qué>, para <por qué>.
Aceptación (cada línea, comprobable sí/no):
- Dado <situación>, cuando <acción>, entonces <resultado>.
Fuera de alcance: <qué NO se hace>
Dudas: [NEEDS CLARIFICATION: <pregunta concreta>]
## Técnico
<ficheros, comandos de verificación, restricciones>
```

Reglas: 1–3 historias; 3–6 criterios; si no caben en 2 KB, la tarjeta es demasiado grande → trocear.
Un agente nuevo debe poder saber qué construir y cuándo parar leyendo solo la tarjeta + la constitución.

## Constitución (plantilla para CLAUDE.md, ≤1 página)
```
## Constitución
1. Propósito: <una frase: para quién y qué problema>.
2. Pila y límites: <lenguajes, dependencias permitidas/prohibidas>.
3. Calidad: todo cambio con test; tests en verde antes de cerrar.
4. Simplicidad: lo mínimo que cumpla los criterios; nada «por si acaso».
5. Quien implementa no evalúa; el tester verifica contra los criterios de aceptación.
6. Dudas: se marcan [NEEDS CLARIFICATION], no se adivinan.
7. Cambios de requisitos: se edita la tarjeta (`board.py desc`) y se anota el porqué con `note`.
```

## Cuándo reconsiderar spec-kit completo
Más de 5 funcionalidades con requisitos cambiantes y varios agentes escribiendo código.
