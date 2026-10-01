# Fisicoquímica

Material para preparar el examen de Fisicoquímica (UADE, prof. Juan M. Alderete).

| Archivo | Qué es |
|---|---|
| `index.html` | Web de estudio: resumen, hoja de fórmulas, ejercicios resueltos, preguntas de teoría y avance. Abrila en el navegador (funciona sin internet). |
| `hoja-de-formulas.pdf` | La hoja para llevar al examen: 2 carillas A4, fórmulas + comentarios cortos + espacio para notas. |
| `resumen.pdf` | Resumen completo por unidad (1 a 10), para leer o pasar a GoodNotes. |

## Unidades

1. Gases reales · 2. Primera ley y calorimetría · 3. Termoquímica · 4. Segunda ley · 5. Equilibrio y electroquímica · 6. Cambios de fase · 7. Mezclas · 8. Cinética · 9. Adsorción y sistemas dispersos · 10. Biorreactores

## Cómo se arma

El contenido está en `src/` (HTML con fórmulas en `$...$`). Para regenerar todo:

```sh
python3 scripts/figuras.py # gráficos SVG del resumen (src/figuras/)
node scripts/build.mjs     # index.html, hoja-de-formulas.html, resumen.html
node scripts/pdf.mjs       # los dos PDF (Playwright + Chromium)
python3 scripts/verificar.py   # recalcula los resultados de los ejercicios
```
