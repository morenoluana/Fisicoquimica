# Fisicoquímica

Material de estudio de Luana para Fisicoquímica (UADE, prof. Alderete). Todo en castellano rioplatense (voseo).

- Contenido fuente en `src/`: `resumen.html`, `formulas.html`, `ejercicios.html`, `preguntas.html` (fórmulas en `$...$`, KaTeX).
- `node scripts/build.mjs` genera `index.html` (web), `hoja-de-formulas.html` y `resumen.html`; `node scripts/pdf.mjs` genera los PDF. Siempre correr los dos después de editar `src/` o `assets/`.
- Gráficos: `scripts/figuras.py` genera `src/figuras/*.html`; se insertan donde `src/resumen.html` dice `<!-- figura: nombre -->`. Colores por unidad en `assets/estilo.css` (`--u1`…`--u10`); tema claro único a propósito.
- Fuentes y KaTeX van embebidos (`assets/fuentes`, `assets/katex`): no usar CDNs, el PDF se genera sin internet.
- `hoja-de-formulas.pdf` tiene que entrar en 2 carillas A4: revisar con `pdfinfo` después de cambiar `src/formulas.html`.
- Ejercicios: cada resultado se verifica en `scripts/verificar.py`. `data-estado="dif"` cuando la guía da otro valor (mostrar el de la guía en `.guia`).
- Simulacros/exámenes que mande Luana: transcribir la consigna en `src/modelos-enunciados.html` (con `data-res` = id de su sección), resolverlos en `src/simulacros.html` y actualizar la tabla "Qué se repite". `modelos-de-examen.pdf` se arma solo con los dos archivos.
